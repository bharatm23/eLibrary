export default {
    template: `<div>
        <div v-if="error">
            <div class='d-flex justify-content-center' style="margin-top: 25vh">
            <div class="mb-3 p-5 bg-light"> 
                {{ error }}
            </div>
            </div>
        </div>

        <h5>User Activity</h5>
        <div class="row">  <div class="col-md-4">  <div class="card mt-2">
            <div class="card-body">
                <p class="card-title">Books Returned: {{ booksReturned }}</p>
            </div>
            </div>
        </div>
        <div class="col-md-4">  <div class="card mt-2">
            <div class="card-body">
                <p class="card-title">Books Issued: {{ booksIssued }}</p>
            </div>
            </div>
        </div>
        <div class="col-md-4">  <div class="card mt-2">
            <div class="card-body">
                <p class="card-title">Book Requests Pending: {{ booksRequested }}</p>
            </div>
            </div>
        </div>
        </div>

        <br><hr><br>
        
        <div class="row">
        <div class="col-sm-6">
            <div class="card w-75 mt-2">
            <div class="card-body">
                <h6 class="card-title">Welcome {{ userDetails.username }}</h6>
                <p class="card-text">Favorite Genre: {{ userDetails.fav_genre }}</p>
                <p class="card-text">Favorite Book: {{ userDetails.fav_book }}</p>
                <p class="card-text">Favorite Authors: {{ userDetails.fav_author }}</p>
                <router-link :to="{ path: '/editUserDetails'}" class="btn btn-secondary">
                        Edit user details</router-link>
            </div>
            </div>
        </div>
        </div>

        <br><hr><br>
        
        <h5>Charts</h5>
        <div v-if="hasChartData">
        <canvas id="barChart"></canvas></div>
        <div v-else-if="!error">No data available for charts.</div>


    </div>`,
    // <router-link :to="{ path: '/editUserDetails', query: { username: userDetails.username } }" class="btn btn-secondary">
    //                     Edit user details</router-link>
    data() {
        return {
            userDetails: [],
            allBooks: [],
            retBooks: [],
            issuedBooks: [],
            reqBooks: [],
            booksReturned: null,
            booksIssued: null,
            booksRequested: null,
            sectionNames: [],
            username: localStorage.getItem('username'),
            token: localStorage.getItem('auth-token'),
            error: null,
            userReturns: [], // [{book_name, rating, (section_name)}, ...]
            hasChartData: false
        }
    },
    created() {
        this.fetchUserDetails()
        this.fetchBooks()
        this.fetchBookReturned()
        this.fetchBookIssued()
        this.fetchBookRequested()
        this.fetchSections()
        this.fetchGraphData()
    },
    watch: {
        hasChartData(newValue) {
            if (newValue) {
                this.$nextTick(() => {
                    this.booksBarChart()
                })
            }
        }
    },
    methods: {
        async fetchUserDetails() {
            try {
                const response = await fetch('/api/userdetails/' + this.username, {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                const userData = await response.json().catch((e) => { })
                if (response.ok) {
                    this.userDetails = userData
                } else (
                    this.error = "Error fetching user data."
                )
            } catch (error) {
                console.log("userDetails error: " + error.message)
                this.error = error.message;
            }
        },
        async fetchBookReturned() {
            try {
                const response = await fetch('/api/returnedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                this.retBooks = await response.json()
                if (response.ok) {
                    this.booksReturned = this.retBooks.filter((ret) => ret.username === this.username).length
                } else (
                    this.error = "Error fetching RETURNED books data."
                )
            } catch (error) {
                console.log("try catch error fetchBookReturned: " + error.message)
                this.error = error.message;
            }
        },
        async fetchBookIssued() {
            try {
                const response = await fetch('/api/issuedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                this.issuedBooks = await response.json()
                if (response.ok) {
                    this.booksIssued = this.issuedBooks.filter((iss) => iss.username === this.username).length
                } else (
                    this.error = "Error fetching ISSUED books data."
                )
            } catch (error) {
                console.log("try catch error fetchBookIssued: " + error.message)
                this.error = error.message
            }
        },
        async fetchBookRequested() {
            try {
                const response = await fetch('/api/requestedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                this.reqBooks = await response.json()
                if (response.ok) {
                    this.booksRequested = this.reqBooks.filter((req) => req.student_username === this.username).length
                } else (
                    this.error = "Error fetching REQUESTED books data."
                )
            } catch (error) {
                console.log("try catch error fetchBookReturned: " + error.message)
                this.error = error.message;
            }
        },
        async fetchBooks() {
            try {
                const response = await fetch('/api/books', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                });
                this.allBooks = await response.json()
                if (!response.ok) {
                    console.log("error fetching books api")
                    this.error = "Error fetching books data."
                } else {
                    // this.issuedBooks and this.allBooks => book_name if this.issuedBooks.username == this.username 
                    // 
                }
            } catch (error) {
                console.log("try catch error fetchMyBooks: " + error.message)
                this.error = error.message;
            }
        },
        async fetchSections() {
            const res = await fetch('/api/sections', {
                headers: {
                    "Authorization": "Bearer " + this.token
                },
            })
            const data = await res.json().catch((e) => { })
            if (res.ok) {
                let allSections = data
                this.sectionNames = allSections.map(section => section.name)
            } else {
                this.error = "403: User is not authorized to view this page."
            }
        },
        async fetchGraphData() {
            const response = await fetch('/api/usergraphs', {
                headers: {
                    "Authorization": "Bearer " + this.token,
                },
            })
            if (response.ok) {
                const graphs = await response.json()
                this.userReturns = graphs // [{book_name, rating, (section_name)}, ...]
                // this.booksBarChart()
                this.hasChartData = this.userReturns.length > 0
            } else {
                this.error = "Error fetching graph details"
            }
        },
        async booksBarChart() {
            const ctx = document.getElementById('barChart').getContext('2d')
            const labels = this.userReturns.map(book => book.book_name)
            const data = this.userReturns.map(book => book.rating)
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Rating',
                            data: data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }],
                        y: {
                            beginAtZero: true,
                        }
                    },
                },
            });
        },
    },
}