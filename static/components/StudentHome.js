export default {
    template: `<div>
        <h5>Available Sections</h5>
        <div class="row">
        <div v-for="section in allSections" :key="section.s_id" class="col-sm-6 col-md-4 col-lg-3"> 
            <div class="card mt-2">
            <div class="card-body d-flex align-items-center justify-content-center"> 
                <h6 class="card-title">{{ section.name }}</h6>
            </div> 
            </div>
        </div>
        </div>

        <br><hr><br>

        <div v-if="error" class='d-flex justify-content-center' style="margin-top: 25vh">
            <div class="mb-3 p-5 bg-light"> {{error}} </div>
        <br><hr><br>
        </div>
        
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

        <div class="row">
        <div class="col-sm-6">
            <div v-for="book in allBooks" :key="book.b_id" class='card mt-2'>
            <div class="card-body">
                <p><h5 class="card-title">Book: {{book.book_name}}</h5></p>
                <p>Author: {{book.authors}}</p>
                <p>Section: {{book.SectionName}}</p> 
                <p>Average Rating: {{book.avgRating}}</p>

                <button class="card-link btn btn-primary mt-2" 
                    :disabled="isBookRequested(book) || book.disableRequest"  
                    @click="requestNewBook(book)">
                    {{ isBookRequested(book) ? 'Book Requested' : 'Request Book' }}
                </button>
            </div>
            </div>
        </div>
        </div>
    </div>`,
    data() {
        return {
            allBooks: [],
            allSections: [],
            token: localStorage.getItem('auth-token'),
            error: null,
            username: localStorage.getItem('username'),
            showTextBox: false
        }
    },
    created() {
        // this.getUserDetails()
        this.fetchAllBooks()
        this.sectionDetails()
    },
    watch: {
        allBooks: {
            handler() {
                this.disableButtons()
            },
            deep: true
        }
    },
    methods: {
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
        async fetchAllBooks() {
            const books = await fetch('/api/books', {
                headers: {
                    "Authorization": "Bearer " + this.token,
                },
            })
            const booksData = await books.json().catch((e) => { })
            if (books.ok) {
                if (booksData.length === 0) {
                    this.error = " There are no books in the database"
                } else {
                    this.allBooks = booksData //0k
                }
            } else {
                this.error = "403: User is not authorized to view this page."
            };
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
        // async getUserDetails() {
        //     const response = await fetch('/auth/whoami', {
        //         headers: {
        //             'Authorization': 'Bearer ' + this.token,
        //         },
        //     })
        //     const user = await response.json().catch((e) => { })
        //     if (response.ok) {
        //         this.username = user.user_details.username //0k
        //     } else {
        //         this.error = "403: User is not authorized to view this page."
        //     }
        // },
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
                // console.log("res not okay: " + JSON.stringify(book))
                // this.error = "Book request to database failed."
                alert('Unable to place request of more than 5 books!')
            }
        },
        async sectionDetails() {
            const res = await fetch('/api/sections', {
                headers: {
                    "Authorization": "Bearer " + this.token
                },
            })
            const data = await res.json().catch((e) => { })
            if (res.ok) {
                if (data.length === 0) {
                    this.error = "There are no sections in the database"
                } else {
                    this.allSections = data
                    // console.log("data: " + JSON.stringify(this.allSections))
                }
            } else {
                this.error = "403: User is not authorized to view this page."
            }
        },
    },
}