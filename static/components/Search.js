export default {
    template: `<div>
    <div v-if="error">
        <div class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light"> 
            {{error}}
        </div>
        </div>
    </div>

    <div v-if="filteredSections.length > 0">
    <h5>Sections by "{{this.searched}}"</h5>
        <div v-for="section in filteredSections" :key="section.s_id">  
            <div class="row">
            <div class="col-sm-6">
                <div class="card w-80 mt-2">
                <div class="card-body">
                <h5 class="card-title">{{section.name}}</h5>
                <p class="card-text">Description: {{section.description}}</p>
                </div>
                </div>
            </div>
            </div>
        </div>
    <br><hr><br>
    </div>

    <div v-if="filteredBooks.length > 0">
        <div v-if="showTextBox" class="mb-3">
            <div class="row">
            <div class="card mt-2">
                <div class="card-body d-flex align-items-center justify-content-center"> 
                    <h6 class="card-title">You cannot request any more books as 5 books have been requested. 
                        Let the librarian respond before you can request any more.
                    </h6>
                </div>
            </div>
            </div>
        </div>

        <h5>Books by "{{this.searched}}"</h5>
        <div v-for="book in filteredBooks" :key="book.b_id"> 
            <div class="row">
            <div class="col-sm-6">
                <div class="card w-75 mt-2">
                <div class="card-body">
                    <h5 class="card-title">{{book.book_name}}</h5>
                    <p class="card-text">Authors: {{book.authors}}</p>
                    <p class="card-text">Section: {{book.SectionName}}</p>
                    <p class="card-text">Average rating: {{book.avgRating}}</p>

                    <button v-if="role=='Student'" class="card-link btn btn-primary mt-2" 
                        :disabled="isBookRequested(book) || book.disableRequest"  
                        @click="requestNewBook(book)">
                        {{ isBookRequested(book) ? 'Book Requested' : 'Request Book' }}
                    </button>
                </div>
                </div>
            </div>
            </div>
        </div>
    </div>
    
    <div v-if="filteredBooks.length === 0 && filteredSections.length === 0">
        <h6>No book or section by "{{this.searched}}"</h6>
    </div>

    <button class="btn btn-secondary mt-2" @click="$router.push('/')">Go Back</button>
</div>`,

    data() {
        return {
            token: localStorage.getItem('auth-token'),
            role: localStorage.getItem('role'),
            error: '',
            searched: '',
            allBooks: [],
            allSections: [],
            showTextBox: false,
            username: localStorage.getItem('username')
        }
    },
    watch: {
        '$route.query.item'(newQuery) {
            this.searched = newQuery;
            this.fetchAllSections();
            this.fetchAllBooks();
        },
        allBooks: {
            handler() {
                this.disableButtons()
            },
            deep: true
        }
    },
    created() {
        this.searched = this.$route.query.item
        this.fetchAllSections()
        this.fetchAllBooks()
        // this.getUserDetails()

    },
    computed: {
        filteredBooks() {
            return this.allBooks.filter(book =>
                book.book_name.toLowerCase().includes(this.searched.toLowerCase()) ||
                book.authors.toLowerCase().includes(this.searched.toLowerCase()) ||
                book.SectionName.toLowerCase().includes(this.searched.toLowerCase())
            )
        },
        filteredSections() {
            return this.allSections.filter(section =>
                section.name.toLowerCase().includes(this.searched.toLowerCase()) ||
                section.description.toLowerCase().includes(this.searched.toLowerCase()))
        },
    },
    methods: {
        // async getUserDetails() {
        //     const response = await fetch('/auth/whoami', {
        //         headers: {
        //             'Authorization': 'Bearer ' + this.token,
        //         },
        //     });
        //     const user = await response.json().catch((e) => { });
        //     if (response.ok) {
        //         this.username = user.user_details.username;
        //     } else {
        //         this.error = "403: User is not authorized to view this page.";
        //     }
        // },
        disableButtons() {
            const requestedCount = this.allBooks.filter(book => this.isBookRequested(book)).length
            this.showTextBox = requestedCount >= 5
            if (requestedCount >= 5) {
                this.allBooks.forEach(book => {
                    if (!this.isBookRequested(book)) {
                        this.$set(book, 'disableRequest', true)
                    } else {
                        this.error = null
                        this.$set(book, 'disableRequest', false)
                    }
                })
            } else {
                this.allBooks.forEach(book => this.$set(book, 'disableRequest', false))
            }
        },
        isBookIssued(book) { //why book.issues?
            return book.issues && book.issues.some(issue => issue.username === this.username)
        },
        isBookRequested(book) {
            if (!Array.isArray(book.requests)) {
                console.log("empty array")
                return false;
            }

            return book.requests.some(request => request.status === 'requested' && request.student_username === this.username) || this.isBookIssued(book)
        },
        async requestNewBook(book) {
            const response = await fetch('/api/requestedbooks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.token,
                },
                body: JSON.stringify({
                    student_username: this.username,
                    book_id: book.b_id,
                    status: "requested",
                    approved: false
                })
            })
            if (response.ok) {
                const newRequest = await response.json()
                const bookIndex = this.allBooks.findIndex(b => b.b_id === book.b_id)
                if (bookIndex !== -1) {
                    if (!Array.isArray(this.allBooks[bookIndex].requests)) {
                        this.$set(this.allBooks[bookIndex], 'requests', [])
                    }
                    this.allBooks[bookIndex].requests.push(newRequest)
                    this.fetchAllBooks()
                }
            } else {
                console.log("res not okay: " + JSON.stringify(book))
                // this.error = "Book request to database failed."
                alert('Unable to place request of more than 5 books!')
            }
        },
        async fetchAllSections() {
            const res1 = await fetch('/api/sections', {
                headers: {
                    "Authorization": "Bearer " + this.token
                },
            })
            const data = await res1.json().catch((e) => { })
            if (res1.ok) {
                if (data.length === 0) {
                    this.error = "There are no sections in the database"
                } else {
                    this.allSections = data
                }
            } else {
                this.error = "403: User is not authorized to view this page."
            }
        },
        async fetchAllBooks() {
            const res2 = await fetch('/api/books', {
                headers: {
                    "Authorization": "Bearer " + this.token
                },
            })
            const data = await res2.json().catch((e) => { })
            if (res2.ok) {
                if (data.length === 0) {
                    this.error = "There are no books in the database"
                } else {
                    this.allBooks = data
                }
            } else {
                this.error = "403: User is not authorized to view this page."
            }
        },
        async getSearch() {
            const response = await fetch('/api/search', {
                headers: {
                    "Authorization": "Bearer " + this.token
                },
            })
            const data = await response.json().catch((e) => { })
            if (response.ok) {
                this.allBooks = data
            } else {
                this.error = "No book found!"
            }
        }
    },
}