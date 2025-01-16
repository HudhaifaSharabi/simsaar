import frappe
from frappe.auth import LoginManager

@frappe.whitelist(allow_guest=True)
def signup(email, name, password, phone, gender):
    if not frappe.db.exists("User", email):
        # Create the user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": name,
            "enabled": 1,
            "new_password": password,
            "gender": gender,
            "mobile_no": phone,
            "user_type": "Website User"
        })
        user.insert(ignore_permissions=True)

        # Log the user in after signup
        login_manager = LoginManager()
        login_manager.authenticate(user=email, pwd=password)
        login_manager.post_login()

        # Set cookies for the session
        frappe.local.response["cookie"] = {
            "sid": frappe.session.sid,
            "expires": None,
            "path": "/",
            "httponly": True,
        }

        return {"message": "User created and logged in successfully"}
    else:
        frappe.throw("Email already registered.")


@frappe.whitelist()
def booking(number_of_rooms):

    # Create the user
    user = frappe.get_doc({
        "doctype": "Booking",
        "number_of_rooms": number_of_rooms,
        "guest_name":frappe.session.user
        
    })
    user.insert(ignore_permissions=True)

    return {"message": "User created and logged in successfully"}
    
