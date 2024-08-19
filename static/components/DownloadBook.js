export default {
    template: `<div> 
    Download book: {{this.$route.query.bname}}
    <br> 
    <button @click='downloadBook'>Download for Credits 50</button>
    <span v-if='is_waiting'>Waiting for download...</span>
    </div>`,
    data() {
        return {
            error: null,
            is_waiting: false,
            book_name: this.$route.query.bname
        }
    },
    methods: {
        async downloadBook() {
            this.is_waiting = true
            const response = await fetch('/download_ebook', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ b_name: this.book_name })
            })
            const data = await response.json()
            if (response.ok) {
                const taskID = data['task-id']
                const interval = setInterval(async () => {
                    const csv_res = await fetch(`/download_ebook_student_csv/${taskID}`)
                    if (csv_res.ok) {
                        this.is_waiting = false
                        clearInterval(interval)
                        window.location.href = `/download_ebook_student_csv/${taskID}`
                    }
                }, 1000)
            }
        }
        // async downloadBook() {
        //     this.is_waiting = true
        //     const response = await fetch('/download-csv')
        //     const data = await response.json()
        //     if (response.ok) {
        //         const taskID = data['task-id']
        //         const interval = setInterval(async () => {
        //             const csv_res = await fetch(`/get_ebook_csv/${taskID}`)
        //             if (csv_res.ok) {
        //                 this.is_waiting = false
        //                 clearInterval(interval)
        //                 window.location.href = `/get_ebook_csv/${taskID}`
        //             }
        //         }, 1000)
        //     }
        // }
    },
}