import LibrarianHome from "./LibrarianHome.js"
import StudentHome from "./StudentHome.js"

export default {
    template: `<div>
        <LibrarianHome v-if="userRole=='Librarian'" />
        <StudentHome v-if="userRole=='Student'" />
    </div>`,
    data() {
        return {
            userRole: localStorage.getItem('role'),
        }
    },
    components: {
        LibrarianHome,
        StudentHome
    },
}