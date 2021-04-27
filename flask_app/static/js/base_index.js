// MODAL LOGIN/REGISTER
var modalLogin = document.getElementById("modal-login")
var loginBody = document.getElementById("modal-body-login")
var registerBody = document.getElementById("modal-body-register")
var registerEmailBody = document.getElementById("modal-body-register-email")
var recuperarSenhaBody = document.getElementById("modal-body-recuperar-email")
var modalTitleText = document.getElementById("modal-title-text")
var divLoginRegister = document.getElementById("login-register-div")
var myModalLogin = new bootstrap.Modal(modalLogin)

// Buttons and links
var buttonLogin = document.getElementById("login-button")
var buttonRegister = document.getElementById("register-button")
var cadastradoLink = document.getElementById("cadastrado-link")
var cadastradoLink2 = document.getElementById("cadastrado-link-2")
var registrarLink = document.getElementById("registrar-link")
var recuperarSenhaLink = document.getElementById("recuperar-senha-link")
var registrarComEmailBtn = document.getElementById("email-register-btn")
var loginButton = document.getElementById("login-btn")
var registerButton = document.getElementById('register-btn')
var enviarRecuperarSenhaButton = document.getElementById("enviar-recuperar-senha-btn")

// Spinners
var loginSpinner = document.getElementById("login-disabled-btn")
loginSpinner.disabled = true
loginSpinner.style.display = 'none'

var registerSpinner = document.getElementById("register-disabled-btn")
registerSpinner.disabled = true
registerSpinner.style.display = 'none'

var enviarRecuperarSenhaSpinner = document.getElementById("enviar-recuperar-senha-disabled-btn")
enviarRecuperarSenhaSpinner.disabled = true
enviarRecuperarSenhaSpinner.style.display = 'none'

// var fabookLoginSpinner = document.getElementById("login-fecebook-spinner")
// fabookLoginSpinner.style.display = 'none'

// var fabookRegisterSpinner = document.getElementById("register-fecebook-spinner")
// fabookRegisterSpinner.style.display = 'none'

buttonLogin.addEventListener('click', setLoginTela, false);
buttonRegister.addEventListener('click', setRegisterTela, false);

// VARIAVEIS GLOBAIS
var current_user;
//

// MODALS DE LOGIN E REGISTRO
function setRegisterTela(){
    modalTitleText.innerHTML = "Cadastrar-se na RapiArt"
    loginBody.style.display = 'none'
    registerBody.style.display = 'block'
    registerEmailBody.style.display = 'none'
    recuperarSenhaBody.style.display = 'none'
    myModalLogin.show()
}

function setLoginTela(){
    modalTitleText.innerHTML = "Faça login em sua conta"
    loginBody.style.display = 'block'
    registerBody.style.display = 'none'
    registerEmailBody.style.display = 'none'
    recuperarSenhaBody.style.display = 'none'
    myModalLogin.show()
}

function setRegisterEmailTela(){
    modalTitleText.innerHTML = "Cadastrar-se na RapiArt"
    loginBody.style.display = 'none'
    registerBody.style.display = 'none'
    registerEmailBody.style.display = 'block'
    recuperarSenhaBody.style.display = 'none'
    myModalLogin.show()
}

function setRecuperarSenhaTela(){
    modalTitleText.innerHTML = "Recuperar senha"
    loginBody.style.display = 'none'
    registerBody.style.display = 'none'
    registerEmailBody.style.display = 'none'
    recuperarSenhaBody.style.display = 'block'
    
    myModalLogin.show()
}
//

// LOGIN USER STATUS
function save_user_status (data) {
    current_user = data
    console.log(current_user)
    if (current_user['status']!="None"){
        buttonLogin.style.display = 'none'
        buttonRegister.style.display = 'none'
    }
    else{
        buttonLogin.style.display = 'block'
        buttonRegister.style.display = 'block'
    }   
} 
function get_user_status(){
    $.ajax({
        url: '/user_login_status',
        type: 'POST',
        dataType: 'json',
        //data: JSON.stringify({'arteId': arteId, 'novoNome': novoNome}),
        contentType: 'application/json',
        success: function (data) {save_user_status(data)},
    });
}
get_user_status()
//

//FORMULARIO DE LOGIN DO INDEX
$(function() {
    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        loginButton.style.display = 'none'
        loginSpinner.style.display = 'block'
        $.ajax({
            url: '/login-index',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify($(this).serializeArray()),
            contentType: 'application/json',
            //beforeSend: function() {},
            success: function(data) {
                $('#formEmailLoginInput').removeClass('is-invalid')
                $('#formPasswordLoginInput').removeClass('is-invalid')
                if (data['status'] == 'Error'){
                    loginSpinner.style.display = 'none'
                    loginButton.style.display = 'block'
                    $('#formPasswordLoginInput').addClass('is-invalid')
                    $('#formEmailLoginInput').addClass('is-invalid')
                }
                else if (data['status'] == 'Success'){
                    get_user_status()
                    loginSpinner.style.display = 'none'
                    loginButton.style.display = 'block'
                    window.window.location.replace("/")
                }
            }
        });
    });
});
//

//FORMULARIO DE REGISTRO DO INDEX
function showPassword() {
    var x = document.getElementById("formPasswordRegisterInput");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
}

$(function() {
    $('#register-form').on('submit', function(e) {
        e.preventDefault();
        registerSpinner.style.display = 'block'
        registerButton.style.display = 'none'
        $.ajax({
            url: '/register-index',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify($(this).serializeArray()),
            contentType: 'application/json',
            //beforeSend: function() {},
            success: function(data) {
                $('#formEmailRegisterInput').removeClass('is-invalid')
                if (data['status'] == 'Error'){
                    registerSpinner.style.display = 'none'
                    registerButton.style.display = 'block'
                    $('#formEmailRegisterInput').addClass('is-invalid')
                }
                else if (data['status'] == 'Success'){
                    registerSpinner.style.display = 'none'
                    registerButton.style.display = 'block'
                    get_user_status()
                    window.window.location.replace("/")
                }
            }
        });
    });
});
//

//FORMULARIO DE RECUPERAÇÂO DE SENHA DO INDEX
$(function() {
    $('#recuperecao-de-senha-form').on('submit', function(e) {
        e.preventDefault();
        enviarRecuperarSenhaSpinner.style.display = 'block'
        enviarRecuperarSenhaButton.style.display = 'none'
        $.ajax({
            url: '/reset_password-index',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify($(this).serializeArray()),
            contentType: 'application/json',
            //beforeSend: function() {},
            success: function(data) {
                $('#formEmailRecSenhaInput').removeClass('is-invalid')
                $('#formEmailRecSenhaInput').removeClass('is-valid')
                if (data['response'] == 'email_error'){
                    enviarRecuperarSenhaSpinner.style.display = 'none'
                    enviarRecuperarSenhaButton.style.display = 'block'
                    $('#formEmailRecSenhaInput').addClass('is-invalid')
                }
                else if (data['response'] == 'success'){
                    $('#formEmailRecSenhaInput').addClass('is-valid')
                    enviarRecuperarSenhaSpinner.style.display = 'none'
                    enviarRecuperarSenhaButton.style.display = 'block'
                    get_user_status()
                }
            }
        });
    });
});
//