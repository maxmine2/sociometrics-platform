var lastField = 0;

function addField() {
    lastField += 1;
    document.getElementById('form').innerHTML += "<div class='answer-inputs' id='answer-input-"+lastField+"'>\n<label for='question"+lastField+"'>Вопрос</label><input id='question"+lastField+"' type='number' class='answer-input'>\n<label for='answer"+lastField+"'>Ответ</label><input id='answer"+lastField+"' type='number' class='answer-input'>\n</div>"
}

function sendForm() {
    var answers = [];
    for (var i = 1; i < document.getElementsByClassName('answer-input'); i++) {
        answers.push([document.getElementsByClassName('question' + i).value, document.getElementsByClassName('answer' + lastField).value]);
    }
    
    var xhr = new XMLHttpRequest;
    xhr.open('POST', '/test/' + document.getElementById('groupid').value + '/add_form/add')
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            var status = xhr.status;
            if (status === 0 || (status >= 200 && status < 400))
            {
                this.open('/test/' + document.getElementById("groupid").value)
            }
        }
    }
    xhr.send('answer=' + JSON.stringify({
        data: {
            "answers": answers
        }
    }))
}