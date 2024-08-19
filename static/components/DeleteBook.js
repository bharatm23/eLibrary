export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">  
    <div class='delete-book'>
        <form @submit.prevent="deleteBook">
            <div class='text-danger'>{{error}}</div> 

            <p> Are you sure you want to delete the book -  {{this.$route.query.name}}?</p> 
            <p>Any Student requests or book issued to students will also be deleted.</p>
            
            <button class="btn btn-primary mt-2" type="submit" > Delete Book </button>
            <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Cancel</button>
        </form>
    </div></div></div>`,
    data() {
        return {
            book: {
                book_name: '',
                content: '',
                authors: '',
                sectionID_link: '',
                avgRating: ''
            },
            error: null,
            token: localStorage.getItem('auth-token')
        }
    },
    async created() {
        this.book.b_id = this.$route.query.id
        this.book.book_name = this.$route.query.name
        await this.bookDetails()
    },
    methods: {
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
                this.book.avgRating = data.avgRating
            } else {
                this.error = "An error occurred while fetching the book details."
            }
        },
        async deleteBook() {
            const res = await fetch('/api/edit_books/' + this.book.b_id, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.token
                },
            })
            if (res.ok) {
                this.$router.go(-1)
            } else {
                this.error = "No data provided to edit."
            }
        }
    }
}