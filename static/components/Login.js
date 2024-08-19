export default {
    template: `
    <div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">
        <form @submit.prevent="login">
        <div class='text-danger'>{{error}}</div>

        <label for="username" class="form-label">Username</label>
        <input type="text" class="form-control" id="username" v-model='cred.username' required="required">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model='cred.password' required="required">
        
        <button class="btn btn-primary mt-2" type="submit" > Login </button>
        <button class="btn btn-secondary mt-2" @click="$router.push('/register')">Register</button>
        </form>
        
    </div>
    </div>
    `,
    data() {
        return {
            cred: {
                username: '',
                password: '',
            },
            error: null,
        }
    },
    methods: {
        async login() {
            const res = await fetch('/auth/user-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.cred),
            })
            const data = await res.json()
            if (res.ok) {
                localStorage.removeItem('logout')
                console.log("Message: " + data.message) //0k
                localStorage.setItem('auth-token', data.tokens.access)
                localStorage.setItem('role', data.role) //0k
                localStorage.setItem('username', data.username) //0k
                this.$router.push({ path: '/', query: { authToken: data.tokens.access } })
            } else {
                console.log("Error: " + data.error)
                this.error = data.error
            }
        },
    },
}