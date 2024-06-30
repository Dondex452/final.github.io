// Retrieve the selected role from local storage or session storage
const selectedRole = localStorage.getItem('userRole') || 'student'; // Default to 'student' if not set

// Set the user role based on the selected role
const userRole = selectedRole;

// Function to show elements for admin only
function showAdminElements() {
    const adminOnlyLinks = document.querySelectorAll('.admin-only');
    adminOnlyLinks.forEach(link => {
        link.style.display = 'block';
    });
}

// Function to show elements for students only
function showStudentElements() {
    const studentOnlyLinks = document.querySelectorAll('.student-only');
    studentOnlyLinks.forEach(link => {
        link.style.display = 'block';
    });
}

// Function to hide elements for admin
function hideAdminElements() {
    const adminOnlyLinks = document.querySelectorAll('.admin-only');
    adminOnlyLinks.forEach(link => {
        link.style.display = 'none';
    });
}

// Function to hide elements for students
function hideStudentElements() {
    const studentOnlyLinks = document.querySelectorAll('.student-only');
    studentOnlyLinks.forEach(link => {
        link.style.display = 'none';
    });
}

// Function to determine which elements to show or hide based on user role
function showHideElementsBasedOnRole() {
    if (userRole === 'admin') {
        showAdminElements();
        hideStudentElements();
    } else if (userRole === 'student') {
        showStudentElements();
        hideAdminElements();
    } else {
        // Handle other roles if needed
    }
}

// Call the function to show/hide elements based on the user role
showHideElementsBasedOnRole();
