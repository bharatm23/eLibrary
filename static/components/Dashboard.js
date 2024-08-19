export default {
    template: `<div><br>
    <div v-if="error">
        <div class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light"> 
            {{ error }}
        </div>
        </div>
    </div>

    <div v-if="studentUsers.length">
    <h5>User Statistics</h5><br>
    <div class="row g-2">
        <div v-for="user in studentUsers" :key="user.id" class="col-md-4">
            <div class="card h-100">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">User: {{ user.username }}</h5>
                    <p class="card-text"><u>Books Requested:</u> {{ getRequestedBooks(user.username) }}</p>
                    <p class="card-text"><u>Preferred Section to request books:</u> {{ getRequestedSection(user.username) }}</p>
                    <p class="card-text"><u>Books Issued:</u> {{ getIssuedBooks(user.username) }}</p>
                    <p class="card-text"><u>Books Returned:</u> {{ getReturnedBooks(user.username) }}</p>
                    <p class="card-text"><u>Highest rated book:</u> {{ getHighestRating(user.username) }}</p>
                    <p class="card-text"><u>Lowest rated book:</u> {{ getLowestRating(user.username) }}</p>
                </div>
            </div>
        </div>
    </div>
    </div>
    <div v-if="error">{{error}}</div>
    <br>
    <div> 
    <p><h5>Download Student Returns Report</h5>
    <br>
    <button class="btn btn-primary mt-2" @click='downloadReport'>Download</button>
    <span v-if='is_waiting'>Waiting for download...</span></p>
    </div>

    <br><hr><br>
    <h5> Charts & other graphs </h5><br>
    <div v-if="hasChartData">
        <h6 style="display: flex; justify-content: center; align-items: center"> 
            Books sorted by highest average rating 
        </h6><br>
        <div style="display: flex; justify-content: center; align-items: center; padding: 0 50px;">
            <canvas id="barChart" style="max-width: 90%;"></canvas>
        </div>
    <br><hr><br>
        <h6 style="display: flex; justify-content: center; align-items: center"> 
            Book info by sections 
        </h6><br>
        <div style="display: flex; justify-content: center; align-items: center; padding: 0 50px;">
            <canvas id="sectionBars" style="max-width: 90%;"></canvas>
        </div>
    </div>
    <div v-else-if="!error">No data available for charts.</div>
    
    </div>`,
    data() {
        return {
            token: localStorage.getItem('auth-token'),
            role: localStorage.getItem('role'),
            error: null,
            ebooks: [],
            userReturns: [],
            userRequests: [],
            userIssues: [],
            studentUsers: [],
            hasChartData: false,
            is_waiting: false
        }
    },
    created() {
        this.fetchGraphData()
    },
    watch: {
        hasChartData(newValue) {
            if (newValue) {
                this.$nextTick(() => {
                    this.booksBarChart();
                    this.booksSectionBars();
                });
            }
        }
    },
    methods: {
        async downloadReport() {
            this.is_waiting = true
            const response = await fetch('/download_csv', {
                headers: {
                    "Authorization": "Bearer " + this.token
                }
            })
            const data = await response.json()
            if (response.ok) {
                const taskID = data['task-id']
                const interval = setInterval(async () => {
                    const csv_res = await fetch(`/download_librarian_csv/${taskID}`)
                    if (csv_res.ok) {
                        this.is_waiting = false
                        clearInterval(interval)
                        window.location.href = `/download_librarian_csv/${taskID}`
                    }
                }, 1000)
            }
        },
        getRequestedBooks(username) {
            const requests = this.userRequests.filter(r => r.username === username)
            return requests.length > 0 ? requests.map(r => r.book_name).join(', ') : '---'
        },

        getRequestedSection(username) {
            const sections = this.userRequests
                .filter(r => r.username === username)
                .map(r => r.section_name)

            const sectionCounts = {}
            sections.forEach(section => {
                sectionCounts[section] = (sectionCounts[section] || 0) + 1
            })

            const preferredSections = Object.entries(sectionCounts)
                .filter(entry => entry[1] === Math.max(...Object.values(sectionCounts)))
                .map(entry => `${entry[0]} (Books - ${entry[1]})`)
                .join(', ')

            return preferredSections || '---'
        },

        getIssuedBooks(username) {
            const issues = this.userIssues.filter(i => i.username === username)
            return issues.length > 0 ? issues.map(i => i.book_name).join(', ') : '---'
        },

        getReturnedBooks(username) {
            const returns = this.userReturns.filter(r => r.username === username)
            return returns.length > 0 ? returns.map(r => r.book_name).join(', ') : '---'
        },

        getHighestRating(username) {
            const userRatings = this.userReturns.filter(r => r.username === username)
                .map(r => ({ book: r.book_name, rating: r.rating }))

            if (userRatings.length === 0) return '---'

            const highestRatedBook = userRatings.reduce((prev, current) => (prev.rating > current.rating) ? prev : current)

            return `${highestRatedBook.book} - Rated: ${highestRatedBook.rating}`
        },

        getLowestRating(username) {
            const userRatings = this.userReturns.filter(r => r.username === username)
                .map(r => ({ book: r.book_name, rating: r.rating }))

            if (userRatings.length === 0) return '---'

            const getLowestRating = userRatings.reduce((prev, current) => (prev.rating < current.rating) ? prev : current)

            return `${getLowestRating.book} - Rated: ${getLowestRating.rating}`
        },

        async fetchGraphData() {
            const response = await fetch('/api/graphs', {
                headers: {
                    "Authorization": "Bearer " + this.token,
                },
            })
            if (response.ok) {
                const graphs = await response.json()
                this.ebooks = graphs[0] //avgRating, book_name, section_name
                this.userReturns = graphs[1] // username, book_name, section_name, avgRating, return_date
                this.userRequests = graphs[2]
                this.userIssues = graphs[3]
                this.studentUsers = graphs[4]
                this.hasChartData = this.ebooks.length > 0 && this.userRequests.length > 0 && this.userReturns.length > 0 && this.userIssues.length > 0

                // this.booksBarChart()
                // this.booksSectionBars()
            } else {
                this.error = "Error fetching graph details"
            }
        },

        async booksSectionBars() {
            const ctx = document.getElementById('sectionBars').getContext('2d')
            const sectionData = {}
            this.userRequests.forEach(request => {
                const sectionName = request.section_name
                if (!sectionData[sectionName]) {
                    sectionData[sectionName] = { requested: 0, issued: 0, returned: 0 }
                }
                sectionData[sectionName].requested++
            })
            this.userIssues.forEach(issue => {
                const sectionName = issue.section_name
                if (!sectionData[sectionName]) {
                    sectionData[sectionName] = { requested: 0, issued: 0, returned: 0 }
                }
                sectionData[sectionName].issued++
            })
            this.userReturns.forEach(returnEntry => {
                const sectionName = returnEntry.section_name
                if (!sectionData[sectionName]) {
                    sectionData[sectionName] = { requested: 0, issued: 0, returned: 0 }
                }
                sectionData[sectionName].returned++
            })
            const labels = Object.keys(sectionData)
            const datasets = [
                {
                    label: 'Books Requested',
                    data: labels.map(label => sectionData[label].requested),
                    backgroundColor: 'rgba(255, 99, 132, 0.7)'
                },
                {
                    label: 'Books Issued',
                    data: labels.map(label => sectionData[label].issued),
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                },
                {
                    label: 'Books Returned',
                    data: labels.map(label => sectionData[label].returned),
                    backgroundColor: 'rgba(255, 205, 86, 0.7)'
                }
            ]
            new Chart(ctx, {
                type: 'bar',
                data: { labels, datasets },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: 'Section Info',
                            font: { size: 18 }
                        }
                    },
                    scales: {
                        x: { stacked: true },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Books',
                                font: { size: 14 }
                            }
                        }
                    }
                }
            })
        },
        async booksBarChart() {
            const ctx = document.getElementById('barChart').getContext('2d')
            const labels = this.ebooks.map(book => book.book_name)
            const data = this.ebooks.map(book => book.avgRating)
            const sortedData = [...this.ebooks].sort((a, b) => b.avgRating - a.avgRating)
            const sortedLabels = sortedData.map(book => book.book_name)
            const sortedValues = sortedData.map(book => book.avgRating)

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sortedLabels,
                    datasets: [
                        {
                            label: 'Average Rating per Book',
                            data: sortedValues,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, max: 6.0 },
                        yAxes: [{ ticks: { beginAtZero: true } }]
                    },
                },
            })
        },
    },
}