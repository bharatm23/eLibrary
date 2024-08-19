export default {
    template: `<div>
        <div v-if="error">
            <div class='d-flex justify-content-center' style="margin-top: 25vh">
            <div class="mb-3 p-5 bg-light"> 
                {{error}}
            </div>
            </div>
        </div>

        <div v-if="empty">
        <div class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light"> 
        <button class="btn btn-primary mt-2" @click="$router.push('/addBook')">Add book</button>
        </div>
        </div>
        </div>
 
        <div v-for="book in allBooks" :key="book.b_id">  
            <div class="row">
            <div class="col-sm-6">
                <div class="card w-75 mt-2">
                <div class="card-body">
                    <h5 class="card-title">{{book.book_name}}</h5>
                    <p class="card-text">Content: {{book.content}}</p>
                    <p class="card-text">Authors: {{book.authors}}</p>
                    <p class="card-text">Genre: {{book.SectionName}}</p>
                    <p class="card-text">Rating: {{book.avgRating}}</p>

                    <span v-if='issuedTo[book.book_name] && issuedTo[book.book_name].length > 0'>
                    <p class="card-text"><u>Issued to:</u></p>
                    <ul v-for="iss in issuedTo[book.book_name]">
                        <li class="card-text">{{iss}}</li>
                    </ul></span>

                    <span v-if='requested[book.book_name] && requested[book.book_name].length > 0'>
                    <p class="card-text"><u>Requested by:</u></p>
                    <ul v-for="req in requested[book.book_name]">
                        <li class="card-text">{{req}}</li>
                    </ul></span>

                    <router-link :to="{ path: '/editBook', query: { name: book.book_name, id: book.b_id } }" class="btn btn-secondary">
                        Edit Book</router-link>
                    <router-link :to="{ path: '/deleteBook', query: { name: book.book_name, id: book.b_id } }" class="btn btn-dark">
                        Delete Book</router-link>
                </div>
                </div>
            </div>
            </div>
        </div>
        <button class="btn btn-secondary mt-2" @click="$router.push('/')">Go Back</button>
        
    </div>`,
    data() {
        return {
            allBooks: [],
            issuedTo: {},
            requested: {},
            token: localStorage.getItem('auth-token'),
            role: localStorage.getItem('role'),
            error: null,
            empty: false
        }
    },
    async mounted() {
        const res = await fetch('/api/books', {
            headers: {
                "Authorization": "Bearer " + this.token
            },
        })
        const data = await res.json().catch((e) => { })
        if (res.ok) {
            if (data.length === 0) {
                this.error = "There are no books in the database"
            } else {
                this.allBooks = data
                for (let book of this.allBooks) {
                    if (book.issues) {
                        for (let issue of book.issues) {
                            if (this.issuedTo[book.book_name]) {
                                this.issuedTo[book.book_name].push(issue.username)
                            } else {
                                this.issuedTo[book.book_name] = [issue.username]
                            }
                        }
                    }
                }

                for (let book of this.allBooks) {
                    if (book.requests) {
                        for (let req of book.requests) {
                            if (this.requested[book.book_name]) {
                                this.requested[book.book_name].push(req.student_username)
                            } else {
                                this.requested[book.book_name] = [req.student_username]
                            }
                        }
                    }
                }
                // console.log("issue: " + JSON.stringify(this.issuedTo))
            }
        } else {
            this.error = "403: User is not authorized to view this page."
        }
    },
}