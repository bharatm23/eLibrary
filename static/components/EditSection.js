export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">    
    <div class='edit-section'>
        <form @submit.prevent="updateSection">
            <div class='text-danger'>{{error}}</div>

            <label for="name" class="form-label mt-2">Section Name</label>
            <input type="text" class="form-control" id="name" v-model='section.name'>

            <label for="description" class="form-label">Description</label>
            <input type="text" class="form-control" id="description" v-model='section.description'>
            
            <button class="btn btn-primary mt-2" type="submit" > Update Section </button>
            <button class="btn btn-secondary mt-2" @click="$router.push('/')">Cancel</button>
        </form>
    </div></div></div>`,
    data() {
        return {
        section: {
            name: '',
            description: ''
        },
        error: null,
        token: localStorage.getItem('auth-token')
        }
    },
    async created() {
        this.section.s_id = this.$route.query.id
        await this.sectionDetails()
    },
    methods: {
        async sectionDetails() {
        const res = await fetch('/api/sections', {
            headers: {
            "Authorization": "Bearer " + this.token
            }
            })
        const data = await res.json()
        if (res.ok) {
            this.section.name = data.name
            this.section.description = data.description
            } else {
                this.error = "An error occurred while fetching the section details."
            }
        },
        async updateSection() { 
        const res = await fetch('/api/edit_sections/' + this.section.s_id, {
            method: 'PATCH',
            headers: {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + this.token
            },
            body: JSON.stringify({
            name: this.section.name,
            description: this.section.description
            })
            })
            if (res.ok) {
                this.$router.push('/')
            } else {
                const data = await res.json()
                this.error = "No data provided to edit."
            }
        }
    }
}
