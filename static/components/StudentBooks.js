export default {
    template: `
    <div>
        <div v-if="error" class='d-flex justify-content-center' style="margin-top: 25vh">
            <div class="mb-3 p-5 bg-light"> {{error}} </div>
        </div>
    
        <div v-else class="row">
            <h6>Books issued</h6>
            <div class="col-sm-6">
                <div v-if="issuedBooks.length > 0">
                    <div v-for="book in issuedBooks" :key="book.issue_id" class='card mt-2'>
                    <div class="card-body">
                        <p><h5 class="card-title">Book: {{book.book_name}}</h5></p>
                        <p class="card-title">Days left to read book: {{book.daysLeft}}</p>
                        
                        <router-link :to="{ path: '/readbook', query: { name: book.book_name } }" class="btn btn-success mt-2" 
                            v-bind:class="{ 'disabled': book.daysLeft === 0 }" v-bind:disabled="book.daysLeft === 0">
                            Read Book
                        </router-link>

                        <router-link :to="{ path: '/downloadbook', query: { user: username, bname: book.book_name } }" 
                            class="btn btn-secondary mt-2"> Download book </router-link>
                        
                        <router-link :to="{ path: '/returnbook', query: { user: username, bname: book.book_name } }" 
                            class="btn btn-dark mt-2"> Return book </router-link>
                    </div>
                    </div>
                </div>
                <div v-else> <p>You have not been issued any books!</p></div>
            <br>
            <h6>Books returned</h6>
                <div v-if="returnedBooks.length > 0">
                    <div class="col-sm-6">
                        <div v-for="book in returnedBooks" :key="book.return_id" class='card mt-2'>
                        <div class="card-body">
                            <p><h5 class="card-title">Book: {{book.book_name}}</h5></p>
                            <p class="card-title">Your rating: {{book.rating}}</p>
                            <p class="card-title">Return Date: {{book.return_date}}</p>
                        </div>
                        </div>
                    <button class="btn btn-success mt-2" @click="$router.go(-1)">Request new book</button>
                    </div>
                </div>
                <div v-else> <p>You have not returned any books!</p></div>
        </div>
    </div></div>`,
    data() {
        return {
            error: null,
            issuedBooks: [],
            returnedBooks: [],
            books: [],
            book_name: '',
            token: localStorage.getItem('auth-token'),
            username: '',
        }
    },
    created() {
        this.getCurrentUser()
        this.fetchIssuedBooks()
        this.fetchReturnedBooks()
    },
    methods: {
        getCurrentUser() {
            const tok = localStorage.getItem('auth-token')
            if (tok) {
                const decoded = jwt_decode(tok)
                this.username = decoded.sub
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
                    const returns = await response.json()
                    this.returnedBooks = returns.filter(ret => ret.username === this.username)
                } else {
                    this.error = "Error fetching returned books."
                }
            } catch (e) {
                this.error = "Network error: " + e.message
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
                    const books = await response.json()
                    this.issuedBooks = books.filter(book => book.username === this.username)
                    console.log(this.issuedBooks.book_name)
                } else {
                    this.error = "Error fetching issued books."
                }
            } catch (e) {
                this.error = "Network error: " + e.message
            }
        },
    },
}