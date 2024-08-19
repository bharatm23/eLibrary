export default {
    template: `<div>
        <div v-if="error" class='d-flex justify-content-center' style="margin-top: 25vh">
            <div class="mb-3 p-5 bg-light"> {{error}} </div>
        </div>
    
        <div class="row">
        <div class="col-sm-6">
            <div class='card mt-2'>
            <div class="card-body">
                <h5 class="card-title">Title: {{book_name}}</h5>
                <h6 class="card-text">Author: {{authors}}</h6>
                <h6 class="card-text">Section Name: {{sectionName}}</h6>

                <p class="card-text"><em>Content:</em> {{content}}</p>

                </div>
                </div>
        </div>
        </div>
        <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Go back</button>
    </div>`,
    data() {
        return {
            book_name: '',
            content: '',
            authors: '',
            sectionName: '',
            error: null,
            token: localStorage.getItem('auth-token'),
        }
    },
    created() {
        this.fetchBookToRead()
    },
    methods: {
        async fetchBookToRead() {
            try {
                const response = await fetch('/api/books', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                if (response.ok) {
                    const read = await response.json()
                    this.book_name = this.$route.query.name
                    const bookToRead = read.filter(book => book.book_name === this.book_name)
                    this.content = bookToRead[0].content
                    this.authors = bookToRead[0].authors
                    this.sectionName = bookToRead[0].SectionName
                } else {
                    this.error = "Error fetching the book."
                }
            } catch (e) {
                this.error = "Network error: " + e.message
            }
        },
    }
}