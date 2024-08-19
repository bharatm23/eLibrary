export default {
    template: `
    <div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">
        <form @submit.prevent="register">
        <div class='text-danger'>{{error}}</div>

        <label for="username" class="form-label mt-2">Username</label>
        <input type="text" class="form-control" id="username" v-model='cred.username' required="required">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model='cred.password' required="required">
        <label for="fav_genre" class="form-label">Favorite Genre</label>
        <input type="fav_genre" class="form-control" id="fav_genre" v-model='cred.fav_genre' required="required">
        <label for="fav_book" class="form-label">Favorite Book</label>
        <input type="fav_book" class="form-control" id="fav_book" v-model='cred.fav_book' required="required">
        <label for="fav_author" class="form-label">Favorite Author</label>
        <input type="fav_author" class="form-control" id="fav_author" v-model='cred.fav_author' required="required">

        <div class="form-check">
        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault" required="required">
        <label class="form-check-label" for="flexCheckDefault" required="required">
            You may request maximum 5 e-books, each for 7 days only. 
        </label>
        </div>

        <button class="btn btn-primary mt-2" type="submit" > Register as Student </button>
        </form>
        <button class="btn btn-secondary mt-2" @click="$router.push('/')">Already signed up?</button>
    </div>
    </div>
    `,
    data() {
        return {
            cred: {
                username: null,
                password: null,
            },
            error: null,
        }
    },
    methods: {
        async register() {
            const res = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.cred),
            })
            const data = await res.json()
            if (res.ok) {
                this.$router.push({ path: '/login' })
            } else {
                this.error = data.error
            }
        },
    },
}