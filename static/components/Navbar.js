export default {
    template: `
        <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
            <span class="navbar-brand">eLibrary</span>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" 
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
        </button>
        <div v-if='is_login' class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

            <li class="nav-item" v-if="role=='Librarian'">
                <router-link :to="{ path: '/dashboard' }" class="nav-link">Dashboard</router-link>
            </li>
            <li class="nav-item" v-if="role=='Librarian'">
                <router-link :to="{ path: '/' }" class="nav-link">Sections</router-link>
            </li>
            <li class="nav-item" v-if="role=='Librarian'">
                <router-link :to="{ path: '/allBooks' }" class="nav-link">Books</router-link>
            </li>
            <li class="nav-item" v-if="role=='Librarian'">
                <router-link :to="{ path: '/studentRequests' }" class="nav-link">Book Requests</router-link>
            </li>

            <li class="nav-item" v-if="role=='Student'">
                <router-link :to="{ path: '/userProfile' }" class="nav-link">{{this.username}}</router-link>
            </li>
            <li class="nav-item" v-if="role=='Student'">
                <router-link :to="{ path: '/' }" class="nav-link">All Books</router-link>
            </li>
            <li class="nav-item" v-if="role=='Student'">
                <router-link :to="{ path: '/studentBooks' }" class="nav-link">My Books</router-link>
            </li>
            
            <li class="nav-item">
                <button class="nav-link" @click='logout'>Logout</button>
            </li>   
        </ul>

        <form class="d-flex" role="search" @submit.prevent="newSearch">
            <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" v-model="searchQuery">
            <button class="btn btn-outline-success" type="submit">
                Search
            </button>
        </form>
        </div>
    </div>
    </nav>`,
    data() {
        return {
            searchQuery: '',
            searched: [],
            role: localStorage.getItem('role'),
            is_login: localStorage.getItem('auth-token'),
            username: localStorage.getItem('username')
        }
    },
    methods: {
        logout() {
            localStorage.removeItem('auth-token')
            localStorage.removeItem('role')
            localStorage.removeItem('username')
            this.$router.push({ path: '/login' })
            const response = fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.is_login
                },
            })
            if (response.ok) {
                localStorage.removeItem('auth-token')
                localStorage.removeItem('role')
                localStorage.removeItem('username')
                this.role = ''
                this.username = ''
                this.is_login = ''
            } else {
                this.error = "Issue with logging out."
            }
        },

        async newSearch() {
            const postResponse = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.is_login
                },
                body: JSON.stringify({
                    item: this.searchQuery
                })
            })
            if (postResponse.ok) {
                this.$router.push({ path: '/search', query: { item: this.searchQuery } })
            } else {
                this.error = "Nothing to search"
            }
        },
    },
}

// logout() {
//     fetch('/auth/logout', {
//         method: 'POST',
//         headers: {
//             'Authorization': `Bearer ${this.is_login}`,
//             'Content-Type': 'application/json' // Add content type header
//         }
//             .then(response => {
//                 if (response.ok) {
//                     localStorage.removeItem('auth-token')
//                     localStorage.removeItem('role')
//                     localStorage.removeItem('username')
//                     this.role = ''
//                     this.username = ''
//                     this.is_login = ''
//                     this.$router.push({ path: '/login' })
//                 }
//             })
//     })
// },
// logout() {
//     localStorage.removeItem('auth-token')
//     localStorage.removeItem('role')
//     localStorage.removeItem('username')
//     this.role = ''
//     this.username = ''
//     this.is_login = ''
//     this.$router.push({ path: '/login' })
// },