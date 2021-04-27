// INTEGRAÇÃO WOOCOMMERCE //
var tabIntegracoes = document.getElementById('tab-integracoes')

var salvarWooBtn = document.getElementById('salvar-btn')
var salvarWooLoading = document.getElementById('salvar-disabled-btn')
var checarWooBtn = document.getElementById('checar-btn')
var checarWooLoading = document.getElementById('checar-disabled-btn')
var responseWooMessage = document.getElementById('woo-response')
var wooCommerceURLInput = document.getElementById('wooCommerceURLInput')
var wooCommerceKeyInput = document.getElementById('wooCommerceKeyInput')
var wooCommerceSecretInput = document.getElementById('wooCommerceSecretInput')

salvarWooLoading.style.display = 'none'
checarWooLoading.style.display = 'none'
responseWooMessage.style.display = 'none'

getIntegracesData();

tabIntegracoes.addEventListener('click', getIntegracesData, false);
salvarWooBtn.addEventListener('click', salvarrWooDados, false);
checarWooBtn.addEventListener('click', checarWooDados, false);

function getIntegracesData(){
    $.ajax({
        url: '/get_key',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify({
            'platform': 'woocommerce'
        }),
        contentType: 'application/json',
        //beforeSend: function() {},
        success: function(data) {
            salvarWooLoading.style.display = 'none'
            salvarWooBtn.style.display = 'block'
            if (data['status'] == 'error'){
                if(data['error_number'] == 1002){
                    responseWooMessage.style.display = 'block'
                    responseWooMessage.style.color = 'red'
                    responseWooMessage.innerHTML = "Erro ao conectar a API. Verifique se os dados estão corretos e tente novamente<br>Se o erro persistir, contato nosso suporte"
                }
            } 
            else{
                wooCommerceURLInput.value = data['store_url']
                wooCommerceKeyInput.value = data['key']
                wooCommerceSecretInput.value = data['secret']
            }
        }
    });
}

function salvarrWooDados(){
    responseWooMessage.style.display = 'none'
    salvarWooBtn.style.display = 'none'
    salvarWooLoading.style.display = 'block'
    $.ajax({
        url: '/save_key',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify({
            'platform': 'woocommerce',
            'store_url': wooCommerceURLInput.value,
            'key': wooCommerceKeyInput.value,
            'secret': wooCommerceSecretInput.value
        }),
        contentType: 'application/json',
        //beforeSend: function() {},
        success: function(data) {
            salvarWooLoading.style.display = 'none'
            salvarWooBtn.style.display = 'block'
            if (data['status'] == 'error'){
                responseWooMessage.style.display = 'block'
                responseWooMessage.style.color = 'red'
                responseWooMessage.innerHTML = "Erro ao conectar a API. Verifique se os dados estão corretos e tente novamente<br>Se o erro persistir, contato nosso suporte"
            } 
            else{  
                responseWooMessage.style.display = 'block'              
                responseWooMessage.style.color = 'green'
                responseWooMessage.innerHTML = "Dados armazenados com sucesso!"
            }
        }
    });
}


function checarWooDados(){
    responseWooMessage.style.display = 'none'
    checarWooBtn.style.display = 'none'
    checarWooLoading.style.display = 'block'
    $.ajax({
        url: '/check_key',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify({
            'platform': 'woocommerce',
            'store_url': wooCommerceURLInput.value,
            'key': wooCommerceKeyInput.value,
            'secret': wooCommerceSecretInput.value
        }),
        contentType: 'application/json',
        //beforeSend: function() {},
        success: function(data) {
            checarWooLoading.style.display = 'none'
            checarWooBtn.style.display = 'block'
            if (data['status'] == 'error'){
                responseWooMessage.style.display = 'block'
                responseWooMessage.style.color = 'red'
                responseWooMessage.innerHTML = "Erro ao conectar a API. Verifique se os dados estão corretos e tente novamente<br>Se o erro persistir, contato nosso suporte"
            } 
            else{  
                responseWooMessage.style.display = 'block'              
                responseWooMessage.style.color = 'green'
                responseWooMessage.innerHTML = "Conexão realizada com sucesso!"
            }
        }
    });
}

function showWooPassword() {
    if (wooCommerceSecretInput.type === "password") {
        wooCommerceSecretInput.type = "text";
    } else {
        wooCommerceSecretInput.type = "password";
    }
}
//////////////////////////////////////////



// ADICIONA ID AS TABS //
$(function(){
    var hash = window.location.hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');
  
    $('.nav-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
        var scrollmem = $('body').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(scrollmem);
    });
  });
/////////////////////////////

// CORRIGI FORMATAÇÂO VINDA DO STRIPE PARA OS VALORES DAS ASSINATURAS //
try{
    var plan_cost_id = document.getElementById('plan_cost')
    var plan_cost = Number(plan_cost_id.innerText);

    var plan_cost_BRL = plan_cost.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'});
    plan_cost_id.innerText = "Valor do plano: " + plan_cost_BRL
}catch(e){}
/////////////////////////////

// FIXA FORMATAÇÂO DO CPF E CELULAR DO USUÁRIO //
$(document).ready(function(){
    var SPMaskBehavior = function (val) {
        return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
    },
    spOptions = {
    onKeyPress: function(val, e, field, options) {
        field.mask(SPMaskBehavior.apply({}, arguments), options);
        }
    };
    
    $('#celular').mask(SPMaskBehavior, spOptions);
    $('#cpf').mask('000.000.000-00');
});

document.querySelector("#cpf").addEventListener("blur", event => {
    var i = document.querySelector("#cpf");
    var v = i.value;
    var test = validaCpfCnpj(i.value);
    if (test == false) {
        i.value = ''
        window.alert('CPF Inválido')
    }
});
/////////////////////////////

// VERIFICADOR DE CPF E CNPJ //
function validaCpfCnpj(val) {
    if (val.length == 14) {
        var cpf = val.trim();
     
        cpf = cpf.replace(/\./g, '');
        cpf = cpf.replace('-', '');
        cpf = cpf.split('');
        
        var v1 = 0;
        var v2 = 0;
        var aux = false;
        
        for (var i = 1; cpf.length > i; i++) {
            if (cpf[i - 1] != cpf[i]) {
                aux = true;   
            }
        } 
        
        if (aux == false) {
            return false; 
        } 
        
        for (var i = 0, p = 10; (cpf.length - 2) > i; i++, p--) {
            v1 += cpf[i] * p; 
        } 
        
        v1 = ((v1 * 10) % 11);
        
        if (v1 == 10) {
            v1 = 0; 
        }
        
        if (v1 != cpf[9]) {
            return false; 
        } 
        
        for (var i = 0, p = 11; (cpf.length - 1) > i; i++, p--) {
            v2 += cpf[i] * p; 
        } 
        
        v2 = ((v2 * 10) % 11);
        
        if (v2 == 10) {
            v2 = 0; 
        }
        
        if (v2 != cpf[10]) {
            return false; 
        } else {   
            return true; 
        }
    } else if (val.length == 18) {
        var cnpj = val.trim();
        
        cnpj = cnpj.replace(/\./g, '');
        cnpj = cnpj.replace('-', '');
        cnpj = cnpj.replace('/', ''); 
        cnpj = cnpj.split(''); 
        
        var v1 = 0;
        var v2 = 0;
        var aux = false;
        
        for (var i = 1; cnpj.length > i; i++) { 
            if (cnpj[i - 1] != cnpj[i]) {  
                aux = true;   
            } 
        } 
        
        if (aux == false) {  
            return false; 
        }
        
        for (var i = 0, p1 = 5, p2 = 13; (cnpj.length - 2) > i; i++, p1--, p2--) {
            if (p1 >= 2) {  
                v1 += cnpj[i] * p1;  
            } else {  
                v1 += cnpj[i] * p2;  
            } 
        } 
        
        v1 = (v1 % 11);
        
        if (v1 < 2) { 
            v1 = 0; 
        } else { 
            v1 = (11 - v1); 
        } 
        
        if (v1 != cnpj[12]) {  
            return false; 
        } 
        
        for (var i = 0, p1 = 6, p2 = 14; (cnpj.length - 1) > i; i++, p1--, p2--) { 
            if (p1 >= 2) {  
                v2 += cnpj[i] * p1;  
            } else {   
                v2 += cnpj[i] * p2; 
            } 
        }
        
        v2 = (v2 % 11); 
        
        if (v2 < 2) {  
            v2 = 0;
        } else { 
            v2 = (11 - v2); 
        } 
        
        if (v2 != cnpj[13]) {   
            return false; 
        } else {  
            return true; 
        }
    } else {
        return false;
    }
 }