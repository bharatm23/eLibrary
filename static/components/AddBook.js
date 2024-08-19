export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light">
            <form @submit.prevent="newBook">
            <div class='text-danger'>{{error}}</div>

            <label for="book_name" class="form-label mt-2">Book Name</label>
            <input type="text" class="form-control" id="book_name" v-model='book.book_name' required="required">
            
            <label for="content" class="form-label mt-2">Content</label>
            <input type="text" class="form-control" id="content" v-model='book.content' required="required">
            
            <label for="authors" class="form-label mt-2">Authors</label>
            <input type="text" class="form-control" id="authors" v-model='book.authors' required="required">

            <label for="sectionName" class="form-label mt-2">Section Name</label>
            <input type="text" class="form-control" id="sectionName" :placeholder="sectionName" readonly>
            
            
            <button class="btn btn-primary mt-2" type="submit"> Add book </button>
            <button class="btn btn-secondary mt-2" @click="$router.push('/')">Cancel</button>
            </form>
        </div>
    </div>`,
    data() {
        return {
            book: {
                book_name: '',
                content: '',
                authors: '',
                sectionID_link: ''
            },
            sectionName: '',
            token: localStorage.getItem('auth-token'),
            error: null,
        }
    },
    created() {
        this.sectionName = this.$route.query.name
        this.book.sectionID_link = this.$route.query.id
    },
    methods: {
        async newBook() {
            const res = await fetch('/api/books', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.token
                },
                body: JSON.stringify(this.book),
            })
            const data = await res.json()
            if (res.ok) {
                this.$router.push({ path: '/' })
            } else {
                this.book.content = '',
                    this.book.authors = ''
                this.error = data.message

            }
        },
    },
}