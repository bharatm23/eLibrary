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
        <button class="btn btn-primary mt-2" @click="$router.push('/addSection')">Add section</button>
        </div>
        </div>
        </div>
        <div>
            <div v-for="section in allSections" :key="section.s_id">  
                <div class="row">
                <div class="col-sm-6">
                    <div class="card w-80 mt-2">
                    <div class="card-body">
                    <h5 class="card-title">{{section.name}}</h5>
                    <p class="card-text">Created on: {{section.date_created}}</p>
                    <p class="card-text">Description: {{section.description}}</p>
                    
                    <router-link :to="{ path: '/sectionBook', query: { id: section.s_id } }" class="btn btn-success">
                        View books</router-link>
                    <router-link :to="{ path: '/addBook', query: { name: section.name, id: section.s_id } }" class="btn btn-primary">
                        Add book</router-link>
                    <router-link :to="{ path: '/editSection', query: { name: section.name, id: section.s_id } }" class="btn btn-secondary">
                        Edit Section</router-link>
                    <router-link :to="{ path: '/deleteSection', query: { name: section.name, id: section.s_id } }" class="btn btn-dark">
                        Delete Section</router-link>
                        
                    </div>
                    </div>
                </div>
                </div>
            </div>
        <button class="btn btn-primary mt-2" @click="$router.push('/addSection')">Add section</button>
        </div>        
    </div>`,
    data () {
        return {
            allSections: [],
            token: localStorage.getItem('auth-token'),
            role: localStorage.getItem('role'),
            error: null,
            empty: false
        }
    },
    async mounted() { 
        const res = await fetch('/api/sections', {
            headers: {
                "Authorization": "Bearer " + this.token
            },
        })
        const data = await res.json().catch((e) => {})
        if(res.ok) {
            this.allSections = data
        } else {
            this.error = "403: User is not authorized to view this page."
        }
    },
}