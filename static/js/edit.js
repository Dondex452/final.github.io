document.addEventListener('DOMContentLoaded', function () {
    // Populate the edit form with the current details
    document.querySelector('[data-target="#editModal"]').addEventListener('click', function () {
        document.getElementById('editSurname').value = document.getElementById('studentSurname').innerText;
        document.getElementById('editFirstName').value = document.getElementById('studentFirstName').innerText;
        document.getElementById('editOtherName').value = document.getElementById('studentOtherName').innerText;
        document.getElementById('editFaculty').value = document.getElementById('studentFaculty').innerText;
        document.getElementById('editPhoneNumber').value = document.getElementById('studentPhoneNumber').innerText;
        document.getElementById('editUsername').value = document.getElementById('studentUsername').innerText;
        // You may choose not to populate the password field for security reasons
    });

    // Handle form submission
    document.getElementById('editForm').addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('studentSurname').innerText = formData.get('surname');
                document.getElementById('studentFirstName').innerText = formData.get('first_name');
                document.getElementById('studentOtherName').innerText = formData.get('other_name');
                document.getElementById('studentFaculty').innerText = formData.get('faculty');
                document.getElementById('studentPhoneNumber').innerText = formData.get('phone_number');
                document.getElementById('studentUsername').innerText = formData.get('username');
                // Update other fields as necessary
                $('#editModal').modal('hide');
            } else {
                alert('An error occurred while saving changes.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
