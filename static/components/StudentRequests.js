export default {
    template: `
    <div>
        <div v-if="error" class='d-flex justify-content-center' style="margin-top: 25vh">
            <div class="mb-3 p-5 bg-light"> {{error}} </div>
        </div>
    
        <div v-else>
            <h5>Books requested</h5>
            <div v-if="requests.length > 0">
            <table class="table">
                <thead>
                    <tr>
                    <th scope="col">Username</th>
                    <th scope="col">Book Name</th>
                    <th scope="col">Actions</th>
                    </tr>
                </thead>
                <tbody>
                <tr v-for="request in sortedRequests" :key="request.request_id">
                
                    <td>{{ request.student_username }}</td>
                    <td>{{ getBookName(request.book_id) }}</td>
                    
                    <td>
                        <button type="button" class="btn btn-success" @click="updateRequest(request.request_id, true)">
                            Approve
                        </button>
                        <button type="button" class="btn btn-danger" @click="updateRequest(request.request_id, false)">
                            Deny
                        </button>
                    </td>
                </tr>
            </tbody></table></div>
            <div v-else> <p>No book requests to display.</p></div>
            
            <br><hr><br>

            <h5>Issued Books</h5>
            <div v-if="issuedBooks.length > 0">
            <table class="table">
                <thead>
                    <tr>
                    <th scope="col">Username</th>
                    <th scope="col">Book Name</th>
                    <th scope="col">Issue Date</th>
                    <th scope="col">Days Left</th>
                    </tr>
                </thead>
                <tbody>
                <tr v-for="issue in sortedIssues" :key="issue.issue_id">
                
                    <td>{{ issue.username }}</td>
                    <td>{{ issue.book_name }}</td>
                    <td>{{ formatDate1(issue.issue_date) }}</td>
                    <td>{{ issue.daysLeft }}</td>
                    
                    <td>
                        
                    </td>
                </tr>
            </tbody></table></div>
            <div v-else> <p>No books issued to display.</p></div>
            
            <br><hr><br>

            <h5>Returned Books</h5>
            <div v-if="returnBooks.length > 0">
            <table class="table">
                <thead>
                    <tr>
                    <th scope="col">Username</th>
                    <th scope="col">Book Name</th>
                    <th scope="col">Rating</th>
                    <th scope="col">Return Date</th>
                    </tr>
                </thead>
                <tbody>
                <tr v-for="ret in sortedReturns" :key="ret.return_id">
                    <td>{{ ret.username }}</td>
                    <td>{{ ret.book_name }}</td>
                    <td>{{ ret.rating }}</td>
                    <td>{{ formatDate(ret.return_date) }}</td>
                </tr>
            </tbody></table></div>
            <div v-else> <p>No books returned yet.</p></div>
        </div>
        <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Go back</button>
    </div>`,

    // <button type="button" class="btn btn-danger" :disabled="issue.daysLeft === 0" @click="revokeBook(issue.issue_id)">
    //                         Revoke Book
    //                     </button>
    data() {
        return {
            requests: [],
            issuedBooks: [],
            returnBooks: [],
            books: [],
            token: localStorage.getItem('auth-token'),
            role: localStorage.getItem('role'),
            error: null
        }
    },
    async mounted() {
        await this.fetchBooks()
        await this.fetchRequests()
        await this.fetchIssuedBooks()
        await this.fetchReturnedBooks()
    },
    computed: {

        sortedRequests() {
            return [...this.requests].sort((a, b) => b.request_id - a.request_id)
        },
        sortedIssues() {
            return [...this.issuedBooks].sort((a, b) => b.issue_id - a.issue_id)
        },
        sortedReturns() {
            return [...this.returnBooks].sort((a, b) => b.return_id - a.return_id)
        }
    },
    methods: {
        formatDate1(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString("en-US", {
                weekday: "short",
                month: "short",
                day:
                    "numeric",
                year: "numeric"
            });
        },
        formatDate(dateString) {
            const date = new Date(dateString)

            if (
                date.getUTCHours() === 0 &&
                date.getUTCMinutes() === 0 &&
                date.getUTCSeconds() === 0
            ) {
                return date.toLocaleDateString("en-US", {
                    weekday: "short",
                    day: "numeric",
                    month: "short",
                    year: "numeric"
                })
            } else {
                return date.toLocaleString("en-US", {
                    weekday: "short",
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                    hour: "numeric",
                    minute: "numeric",
                    timeZoneName: "short",
                })
            }
        },
        async fetchReturnedBooks() {
            try {
                const response = await fetch('/api/returnedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                if (response.ok) {
                    this.returnBooks = await response.json()
                    console.log("fetchRetBooks: " + this.returnBooks)
                } else {
                    console.log("error in fetchReturnedBooks: " + error.message)
                    this.error = error.message
                }
            } catch (error) {
                console.log("try catch error fetchReturnedBooks: " + error.message)
                this.error = error.message
            }
        },
        async fetchIssuedBooks() {
            try {
                const response = await fetch('/api/issuedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                if (response.ok) {
                    this.issuedBooks = await response.json()
                    // console.log("fetchIssuedBooks: " + this.issuedBooks)
                } else {
                    console.log("error in fetchIssuedBooks: " + error.message)
                    this.error = error.message
                }
            } catch (error) {
                console.log("try catch error fetchIssuedBooks: " + error.message)
                this.error = error.message
            }
        },
        async fetchRequests() {
            try {
                const response = await fetch('/api/requestedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                if (response.ok) {
                    this.requests = await response.json()
                    // console.log("fetchRequests (current req): " + this.requests)
                } else {
                    console.log("error in fetchRequests: " + error.message)
                    this.error = error.message
                }
            } catch (error) {
                console.log("try catch error fetchRequests: " + error.message)
                this.error = error.message
            }
        },
        async fetchBooks() {
            try {
                const response = await fetch('/api/books', {
                    headers: {
                        "Authorization": "Bearer " + localStorage.getItem('auth-token'),
                    },
                });
                if (!response.ok) throw new Error('Failed to fetch books')
                this.books = await response.json()
            } catch (error) {
                console.log("try catch error fetchBooks: " + error.message)
                this.error = error.message;
            }
        },
        getBookName(bookId) { //WHY THIS?
            const book = this.books.find(b => b.b_id === bookId)
            // console.log("getBookName: " + book)
            return book ? book.book_name : 'Unknown'
        },
        async revokeBook(issuedID) {
            try {
                const revoke_daysLeft = "0"
                const response = await fetch(`/api/edit_issuedbooks/${issuedID}`, {
                    method: 'PATCH',
                    headers: {
                        "Authorization": "Bearer " + this.token,
                        "role": this.role,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        daysLeft: revoke_daysLeft
                    }),
                })
                if (response.ok) {
                    this.issuedBooks = this.issuedBooks.filter(i => i.issued_id !== issuedID)
                    await this.fetchIssuedBooks()
                    this.$forceUpdate()
                } else {
                    const error = await response.json()
                    console.log("revokeBook failed to patch IssuedBooks: " + revoke_daysLeft)
                    console.log("revokeBook failed to patch IssuedBooks:", error)
                    this.error = error.message
                }
            } catch (e) {
                console.error("Network error:", e)
                this.error = e.message
            }
        },
        async updateRequest(request, approval) {
            try {
                const book_ID = this.requests.find(r => r.request_id === request).book_id //0k
                const user = this.requests.find(r => r.request_id === request).student_username //0k
                const response = await fetch(`/api/edit_requestedbooks/${request}`, {
                    method: 'PATCH',
                    headers: {
                        "Authorization": "Bearer " + this.token,
                        "role": this.role,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        student_username: user,
                        book_id: book_ID,
                        status: approval ? "approved" : "declined"
                    }),
                })
                if (response.ok) {
                    this.requests = this.requests.filter(r => r.request_id !== request)
                    await this.fetchIssuedBooks()
                    this.$forceUpdate()
                } else {
                    const error = await response.json()
                    console.log("updateRequest failed to patch ReqBooks: " + error)
                    this.error = error.message
                }
            } catch (error) {
                this.error = error.message
            }
        },
    },
}