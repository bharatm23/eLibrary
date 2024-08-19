export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
    <div class="mb-3 p-5 bg-light">    
    <div class='delete-section'>
        <form @submit.prevent="deleteSection">
            <div class='text-danger'>{{error}}</div> 

            <p> Are you sure you want to delete section - {{section.name}}? All associated books will be deleted as well! </p>
            
            <button class="btn btn-primary mt-2" type="submit" > Delete Section </button>
            <button class="btn btn-secondary mt-2" @click="$router.push('/')">Cancel</button>
        </form>
    </div></div></div>`,
    data() {
        return {
            section: {
                s_id: '',
                name: '',
                description: ''
            },
            error: null,
            token: localStorage.getItem('auth-token')
        }
    },
    async created() {
        this.section.s_id = this.$route.query.id
        this.section.name = this.$route.query.name
        await this.fetchsectionDetails()
    },
    methods: {
        async fetchsectionDetails() {
            const res = await fetch('/api/sections', {
                headers: {
                    "Authorization": "Bearer " + this.token
                }
            })
            const data = await res.json()
            if (res.ok) {
            } else {
                this.error = "An error occurred while fetching the section details."
            }
        },
        async deleteSection() {
            try {
                const res = await fetch('/api/edit_sections/' + this.section.s_id, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        "Authorization": "Bearer " + this.token
                    }
                })
                if (!res.ok) {
                    throw new Error('Failed to delete section')
                }
                this.$router.push('/')
            } catch (error) {
                this.error = error.message
            }
        }
    }
}
