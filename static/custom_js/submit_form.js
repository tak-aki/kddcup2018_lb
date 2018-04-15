function check_blank_submit(frm){
if(frm.elements["username"].value=="" || frm.elements["submit_file"].value==""){
return false;
}
}

function check_blank_mysubmission(frm){
if(frm.elements["username"].value==""){
return false;
}
}