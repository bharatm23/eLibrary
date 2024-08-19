export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">    
    <div class='edit-user'>
        
        <h5>Edit User Details</h5>

        <form @submit.prevent="updateUser">
            <div class='text-danger'>{{error}}</div>
            <label for="fav_genre" class="form-label mt-2">Favorite Genre</label>
            <input type="text" class="form-control" id="fav_genre" :placeholder="userDeets.f_genre" v-model='user.fav_genre'>
            
            <label for="fav_book" class="form-label">Favorite Book</label>
            <input type="text" class="form-control" id="fav_book" :placeholder="userDeets.f_book" v-model='user.fav_book'>
            
            <label for="fav_author" class="form-label">Favorite Author</label>
            <input type="text" class="form-control" id="fav_author" :placeholder="userDeets.f_author" v-model='user.fav_author'>
            
            <button class="btn btn-primary mt-2" type="submit" > Update User Details </button>
        </form>
        <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Cancel</button>
    </div></div></div>`,
    data() {
        return {
            username: localStorage.getItem('username'),
            token: localStorage.getItem('auth-token'),
            error: null,
            userDeets: {
                f_genre: '',
                f_book: '',
                f_author: ''
            },
            user: {
                fav_genre: '',
                fav_book: '',
                fav_author: ''
            },
        }
    },
    async created() {
        await this.fetchUserDetails()
    },
    methods: {
        async fetchUserDetails() {
            const res = await fetch('/api/userdetails/' + this.username, {
                headers: {
                    "Authorization": "Bearer " + this.token
                }
            })
            const data = await res.json()
            if (res.ok) {
                this.userDeets.f_genre = data.fav_genre
                this.userDeets.f_book = data.fav_book
                this.userDeets.f_author = data.fav_author
                console.log('user details: ' + JSON.stringify(this.userDeets))
            } else {
                this.error = "An error occured while fetching the user details."
            }
        },
        async updateUser() {
            const res = await fetch('/api/editUser/' + this.username, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.token
                },
                body: JSON.stringify({
                    fav_genre: this.user.fav_genre,
                    fav_book: this.user.fav_book,
                    fav_author: this.user.fav_author
                })
            })
            if (res.ok) {
                this.$router.go(-1)
                console.log('res details: ' + JSON.stringify(this.body))
            } else {
                const data = await res.json()
                this.error = data.message
                console.log('else error: ' + JSON.stringify(this.body))
            }
        }
    }
}