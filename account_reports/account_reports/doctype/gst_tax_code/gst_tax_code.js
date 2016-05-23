

cur_frm.fields_dict['account_head'].get_query = function(doc) {
	return{
		filters:[
			['Account', 'gst_type', 'in', '-GST Input, -GST Output']
		]
	}
}