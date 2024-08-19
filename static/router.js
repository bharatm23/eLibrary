import Home from "./components/Home.js"
import Login from "./components/Login.js"
import Register from "./components/Register.js"
import StudentRequests from "./components/StudentRequests.js"
import AddSection from "./components/AddSection.js"
import AddBook from "./components/AddBook.js"
import EditSection from "./components/EditSection.js"
import allBooks from "./components/AllBooks.js"
import SectionBook from "./components/SectionBook.js"
import DeleteSection from "./components/DeleteSection.js"
import EditBook from "./components/EditBook.js"
import DeleteBook from "./components/DeleteBook.js"
import StudentBooks from "./components/StudentBooks.js"
import BookContent from "./components/BookContent.js"
import ReturnBook from "./components/ReturnBook.js"
import Search from "./components/Search.js"
import UserProfile from "./components/UserProfile.js"
import Dashboard from "./components/Dashboard.js"
import DownloadBook from "./components/DownloadBook.js"
import EditUserDetails from "./components/EditUserDetails.js"

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/login', name: 'Login', component: Login },
    { path: '/register/', name: 'Register', component: Register },
    { path: '/studentRequests', name: 'StudentRequests', component: StudentRequests },
    { path: '/addSection', name: 'AddSection', component: AddSection },
    { path: '/addBook', name: 'AddBook', component: AddBook },
    { path: '/editSection/', name: 'EditSection', component: EditSection },
    { path: '/allBooks/', name: 'allBooks', component: allBooks },
    { path: '/sectionBook/', name: 'SectionBook', component: SectionBook },
    { path: '/deleteSection/', name: 'DeleteSection', component: DeleteSection },
    { path: '/editBook/', name: 'EditBook', component: EditBook },
    { path: '/deleteBook/', name: 'DeleteBook', component: DeleteBook },
    { path: '/studentBooks/', name: 'StudentBooks', component: StudentBooks },
    { path: '/readbook/', name: 'BookContent', component: BookContent },
    { path: '/returnbook/', name: 'ReturnBook', component: ReturnBook },
    { path: '/search/', name: 'Search', component: Search },
    { path: '/UserProfile/', name: 'UserProfile', component: UserProfile },
    { path: '/dashboard/', name: 'Dashboard', component: Dashboard },
    { path: '/downloadbook/', name: 'DownloadBook', component: DownloadBook },
    { path: '/editUserDetails/', name: 'EditUserDetails', component: EditUserDetails }
]

export default new VueRouter({
    routes,
})