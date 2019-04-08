function send_ajax(){
    var xhr = null;
    if(window.XMLHttpRequest){
        xhr = new window.XMLHttpRequest();
    }else{
        xhr = new ActiveXObject("Microsoft.XMLHttp");
    }

    console.log("xhr", xhr)
    xhr.open('get', 'http://127.0.0.1:5000/register/?name=gaozhen', true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            res = xhr.responseText;
            console.log(res)
        }
    };
    xhr.setRequestHeader("Content-type", "application/json")
    xhr.send(null);
}


function send_ajax1(){
    $.ajax
}