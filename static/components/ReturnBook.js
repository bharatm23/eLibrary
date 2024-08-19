export default {
    template: `<div>
    <div v-if="error" class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light"> {{error}} </div>
    </div>
    
    <div v-else>
            <form @submit.prevent="returnBook">
            <div class='text-danger'>{{error}}</div>

            <h6>Return book: {{book_name}}?</h6>
            
            <label for="rating" class="form-label mt-2">Rate between 1-5</label>
            <input type="number" step="0.1" min="1" max="5" class="form-control" id="rating" v-model="rating" required="required">
            
            <button class="btn btn-primary mt-2" type="submit"> Return book </button>
            <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Go back</button>
            </form>
    </div>
    </div>`,
    data() {
        return {
            token: localStorage.getItem('auth-token'),
            issue_ID: null,
            book_name: '',
            username: '',
            rating: null,
            return_date: null,
            error: null,
        }
    },
    created() {
        this.fetchIssueID()
        this.book_name = this.$route.query.bname
        this.username = this.$route.query.user
    },
    methods: {
        async fetchIssueID() {
            try {
                const response = await fetch('/api/issuedbooks', {
                    headers: {
                        "Authorization": "Bearer " + this.token,
                    },
                })
                if (response.ok) {
                    const issued = await response.json()
                    const dateHeader = response.headers.get('date')
                    this.return_date = new Date(dateHeader).toISOString().split('T')[0] //0k - Todays date - 2024-04-25
                    const issuedID = issued.filter(issue => issue.book_name === this.book_name
                        && issue.username === this.username)
                    this.issue_ID = issuedID[0].issue_id //0k
                } else {
                    this.error = "Error fetching the book."
                }
            } catch (e) {
                this.error = "Network error: " + e.message
            }
        },
        async returnBook() {
            try {
                const rtg = parseFloat(this.rating)
                const response = await fetch('/api/returnedbooks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        "Authorization": "Bearer " + this.token,
                    },
                    body: JSON.stringify({
                        issue_ID: this.issue_ID,
                        book_name: this.book_name,
                        username: this.username,
                        rating: rtg,
                        return_date: this.return_date
                    })
                })
                if (!response.ok) {
                    console.log(issue_ID)
                    console.log(book_name)
                    console.log(username)
                    console.log(rating)
                    this.error = 'Failed to send return request'
                } else {
                    this.$router.go(-1)
                }
            } catch (e) {
                this.error = "Network error: " + e.message
            }
        }
    },
}