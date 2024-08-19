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
                <h5> No books in this section </h5>
            <button class="btn btn-primary mt-2" @click="$router.push('/addBook')">Add book</button>
            </div>
            </div>
        </div>
        
        <div v-for="book in sortedBooks" :key="book.b_id"> 
            <div class="row">
            <div class="col-sm-6">
                <div class="card w-75 mt-2">
                <div class="card-body">
                    <h5 class="card-title">{{book.book_name}}</h5>
                    <p class="card-text">Content: {{book.content}}</p>
                    <p class="card-text">Authors: {{book.authors}}</p>
                    <p class="card-text">Section: {{book.SectionName}}</p>
                    <p class="card-text">Rating: {{book.avgRating}}</p>
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
        // <div v-for="book in books" :key="book.b_id">  
        return {
            books: [],
            error: null,
            token: localStorage.getItem('auth-token'),
            empty: false
        }
    },
    async created() {
        await this.fetchBooks();
    },
    computed: {
        sortedBooks() {
            return [...this.books].sort((a, b) => b.b_id - a.b_id)
        }
    },
    methods: {
        async fetchBooks() {
            const sectionId = this.$route.query.id
            const res = await fetch(`/api/sections/${sectionId}/books`, {
                headers: {
                    "Authorization": "Bearer " + this.token
                }
            })
            const data = await res.json()
            if (res.ok && data.length > 0) {
                this.books = data
            } else {
                this.error = "Section with this ID has no books.";
            }
        }
    }
}
