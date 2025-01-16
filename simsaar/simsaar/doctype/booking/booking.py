# Copyright (c) 2025, hudhaifa alsharabi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Booking(Document):
	def before_insert(self):
    # الحصول على اسم المستخدم من الجلسة
		current_user = frappe.session.user

		if current_user == 'Guest':
			frappe.throw("يرجى تسجيل الدخول قبل الحجز.")  # في حالة لم يكن المستخدم مسجلًا

		self.guest_name = frappe.session.user


