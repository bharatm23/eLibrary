export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">    
    <div class='edit-book'>
        <h5>Edit book</h5>
        <form @submit.prevent="updateBook">
            <div class='text-danger'>{{error}}</div>
            <label for="name" class="form-label mt-2">Book Name</label>
            <input type="text" class="form-control" id="name" v-model='book.book_name'>
            
            <label for="content" class="form-label">Content</label>
            <input type="text" class="form-control" id="content" v-model='book.content'>
            
            <label for="authors" class="form-label">Authors</label>
            <input type="text" class="form-control" id="authors" v-model='book.authors'>
            
            <label for="sectionID" class="form-label">Section ID</label>
            <input type="text" class="form-control" id="sectionID" v-model='book.sectionID_link'>
            <small><p>Current sections and their IDs:</p>
            <ul>
                <li v-for="(id, sectionName) in sections" :key="id">
                {{ sectionName }} (ID: {{ id }})
                </li>
            </ul></small>

            <button class="btn btn-primary mt-2" type="submit" > Update Book Details </button>
            <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Cancel</button>
        </form>
    </div></div></div>`,
    data() {
        return {
            book: {
                book_name: '',
                content: '',
                authors: '',
                sectionID_link: ''
            },
            error: null,
            token: localStorage.getItem('auth-token'),
            sections: {}
        }
    },
    async created() {
        this.book.b_id = this.$route.query.id
        this.book.book_name = this.$route.query.name
        await this.bookDetails()
        this.fetchSections()
    },
    methods: {
        async fetchSections() {
            const res = await fetch('/api/sections', {
                headers: {
                    "Authorization": "Bearer " + this.token
                },
            })
            const data = await res.json().catch((e) => { })
            if (res.ok) {
                this.sections = {}
                data.forEach((section) => { this.sections[section.name] = section.s_id })
            } else {
                this.error = "403: User is not authorized to view this page."
            }
        },
        async bookDetails() {
            const res = await fetch('/api/books', {
                headers: {
                    "Authorization": "Bearer " + this.token
                }
            })
            const data = await res.json()
            if (res.ok) {
                this.book.book_name = data.book_name
                this.book.content = data.content
                this.book.authors = data.authors
                this.book.sectionID_link = data.sectionID_link
            } else {
                this.error = "An error occured while fetching the book details"
            }
        },
        async updateBook() {
            const res = await fetch('/api/edit_books/' + this.book.b_id, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.token
                },
                body: JSON.stringify({
                    book_name: this.book.book_name,
                    content: this.book.content,
                    authors: this.book.authors,
                    sectionID_link: this.book.sectionID_link
                })
            })
            if (res.ok) {
                this.$router.go(-1)
            } else {
                const data = await res.json()
                this.error = data.message
                this.book.content = '',
                    this.book.authors = ''
                // this.error = "No data provided to edit."
            }
        }
    }
}