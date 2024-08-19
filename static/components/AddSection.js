export default {
    template: `<div class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light">
            <form form @submit.prevent="newSection">
            <div class='text-danger'>{{error}}</div>

            <label for="name" class="form-label mt-2">Section Name</label>
            <input type="text" class="form-control" id="name" v-model='sect.name' required="required">
            <label for="description" class="form-label">Description</label>
            <input type="text" class="form-control" id="description" v-model='sect.description' required="required">
            <button class="btn btn-primary mt-2" type="submit" > Add section </button>
            <button class="btn btn-secondary mt-2" @click="$router.go(-1)">Cancel</button>
            </form>
        </div>
    </div>`,
    data() {
        return {
            sect: {
                name: null,
                description: null
            },
            token: localStorage.getItem('auth-token'),
            error: null,
        }
    },
    methods: {
        async newSection() {
            const res = await fetch('/api/sections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + this.token
                },
                body: JSON.stringify(this.sect),
            })
            const data = await res.json()
            if (res.ok) {
                this.$router.go(-1)
                // this.$router.push({ path: '/' })
                console.log('res ok: ' + JSON.stringify(this.body))
            } else {
                this.error = data.message
                console.log('bad res: ' + JSON.stringify(this.body))
            }
        },
    },
}