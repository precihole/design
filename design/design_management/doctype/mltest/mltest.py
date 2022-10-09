# Copyright (c) 2022, Precihole and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from textblob import TextBlob

# class MLTest(Document):
# 	def before_save(self):
# 		#Determining the Polarity 
# 		p_1 = TextBlob(str(self.remark)).sentiment.polarity
# 		# p_2 = TextBlob(text_2).sentiment.polarity
# 		#Determining the Subjectivity
# 		# s_1 = TextBlob(text_1).sentiment.subjectivity
# 		# s_2 = TextBlob(text_2).sentiment.subjectivity
# 		if p_1 > 0:
# 			self.test = 'Positive'
# 		elif p_1 == 0:
# 			self.test = 'Neutral'
# 		elif p_1 < 0:
# 			self.test = 'Negative'
# 	pass
