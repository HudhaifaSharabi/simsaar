# Copyright (c) 2025, hudhaifa alsharabi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Booking(Document):
	pass


# Copyright (c) 2025, hudhaifa alsharabi and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class Booking(Document):
# 	pass
# 	def validate(doc, method):
#     # الحصول على اسم المستخدم من الجلسة
#     current_user = frappe.session.user

#     if current_user == 'Guest':
#         frappe.throw("يرجى تسجيل الدخول قبل الحجز.")  # في حالة لم يكن المستخدم مسجلًا

#     doc.guest_name = current_user
