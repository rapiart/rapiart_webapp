document.onreadystatechange = function () {
    if (document.readyState == "complete") {     
        var divModeloEscolhido = document.getElementById("div-modelo-escolhido")
        var divFundoEscolhido = document.getElementById("div-fundo-escolhido")
        var cardsModelos = document.getElementsByClassName("cards-modelos")
        var cardsFundos = document.getElementsByClassName("cards-fundos")
        var btnMudarCor = document.getElementsByClassName("mudar-cor")
        var btnMudarFonte = document.getElementsByClassName("mudar-fonte")
        // var searchForm = document.getElementById("search-form-div")
        var paginationNav = document.getElementById("pagination-nav")
        var modalModelos = document.getElementById("modal-modelos")
        var myModalModelos = new bootstrap.Modal(modalModelos)
        var modalFundos = document.getElementById("modal-fundos")
        var myModalFundos = new bootstrap.Modal(modalFundos)
        var modalUploads = document.getElementById("modal-upload")
        var myModalUploads = new bootstrap.Modal(modalUploads)
        var modalImportar = document.getElementById("modal-importar")
        var myModalImportar = new bootstrap.Modal(modalImportar)
        var iframeModalModelos = document.getElementById("iframe-modal-modelos")
        var iframeModalFundos = document.getElementById("iframe-modal-fundos")
        var myColapseFundo = new bootstrap.Collapse(document.getElementById("collapseFundo"), {toggle: false})
        var myColapseModelo = new bootstrap.Collapse(document.getElementById("collapseModelo"), {toggle: false})
        var myColapseConteudo = new bootstrap.Collapse(document.getElementById("collapseConteudo"), {toggle: false})
        var formSelector = document.getElementById("exampleFormControlSelect1")
        var divSelecionarModelo = document.getElementById("modelosGalery")
        var divSelecionarFundo = document.getElementById("div-fundo-nao-escolhido")
        var btnEditarConteudoModelos = document.getElementById("btn-editar-conteudo-modelos")
        var btnEditarConteudoFundos = document.getElementById("btn-editar-conteudo-fundos")
        var btnTrocarModelo = document.getElementById("btn-trocar-modelo")
        var btnTrocarFundo = document.getElementById("btn-trocar-fundo")
        var btnEscolherModelo = document.getElementById("btn-escolher-modelo")
        var btnEscolherFundo = document.getElementById("btn-escolher-fundo")
        var inputNomeProduto = document.getElementById("input-nome-produto")
        var inputTextoSite = document.getElementById("input-texto-site")
        var inputMensagem = document.getElementById("input-mensagem")
        var inputPrecoNormal = document.getElementById("input-preco-normal")
        var inputPrecoDesconto = document.getElementById("input-preco-desconto")
        var inputImageProduto = document.getElementById("input-product-image")
        var inputImageLogo = document.getElementById("input-logo-image")
        var previewButton = document.getElementById('preview-button')
        var resultImg = document.getElementById('resultImg')
        var loadingButton = document.getElementById('loading-button')
        var divEditarConteudo = document.getElementById('div-editar-conteudo')
        var divNaoEditarConteudo = document.getElementById('div-nao-editar')
        var infoForm = document.getElementById('info-upload')
        var divMensagem = document.getElementById('div-mensagem')
        var divImagemProduto = document.getElementById('div-imagem-produto')
        var divPrecoDesconto = document.getElementById('div-preco-desconto')
        var divPrecoNormal = document.getElementById('div-preco-normal')
        var divNomeProduto = document.getElementById('div-nome-produto')
        var imgProduto = document.getElementById('img-produto')
        var imgLogo = document.getElementById('img-logo')
        var divTextoSite = document.getElementById('div-website')
        var divTextoTelefone = document.getElementById('div-telefone')
        var divTextoEmail = document.getElementById('div-email')
        var divImagemLogo = document.getElementById('div-imagem-logo')
        var divEndereco = document.getElementById('div-endereco')
        var divNomeEmpresa = document.getElementById('div-nome-empresa')
        var divFacebook = document.getElementById('div-facebook')
        var divInstagram = document.getElementById('div-instagram')
        //var tabClicked = document.getElementById("nav-tabs")
        var tabClicked = document.getElementById("nav-tabs-file-type")
        var selectorElement = document.getElementById("selector-tabs")
        var imgFundo = document.getElementById("img-fundo")
        var imgModelo = document.getElementById("img-modelo")
        var inputDuracao = document.getElementById("duracao")
        var duracaoOutput = document.getElementById("duracao-output")
        var videoJsFundos = videojs("div-video-fundos");
        var divNaoEditarModelo = document.getElementById("div-nao-editar-modelo");
        var inputNomeEmpresa = document.getElementById("input-nome-empresa")
        var inputTelefone = document.getElementById("input-telefone")
        var inputEmail = document.getElementById("input-email")
        var inputEndereco = document.getElementById("input-endereco")
        var inputFacebook = document.getElementById("input-facebook")
        var inputInstagram = document.getElementById("input-instagram")
        var imgFundoModal = document.getElementById('img-fundo-modal')
        var divVideoWrapper = document.getElementById('video-wrapper')
        var paginaNumeroFundos = document.getElementById('pagina-numero-fundos')
        var paginaProximoFundos = document.getElementById('pagina-proximo-fundos')
        var paginaVoltarFundos = document.getElementById('pagina-voltar-fundos')
        var btnImportarWoo = document.getElementById('importar-woocommerce')
        var btnImportarProduto = document.getElementById('btn-importar-produto')
        var btnPesquisarProduto = document.getElementById('btn-pesquisa-produto')
        var inputProduto = document.getElementById('input-produto')
        var divResultadoPesquisa = document.getElementById('resultado-pesquisa')
        var wooSpinner = document.getElementById("woo-spinner")
        var divImportarProduto = document.getElementById("div-importar-produto")
        var uploadBtn = document.getElementById("upload-btn")
        var imgUploadFeedback = document.getElementById("img-upload-feedback")
        var imgUploadInput = document.getElementById("img-upload-input")
        var enviarFundoBtn = document.getElementById("btn-enviar-fundo")
        var cropper = ''

        videoJsFundos.fill(true);
        var pagina = 1
        var paginasTotal;
        var paginaAtual;
        var file_type;
        var tab_id;
        
        btnImportarProduto.addEventListener('click', function() { popularInputs() })
        btnPesquisarProduto.addEventListener('click', function() { pesquisarProduto(this) })
        btnImportarWoo.addEventListener('click', function() { myModalImportar.show() })
        paginaProximoFundos.addEventListener('click', function() { mudar_pagina_fundos(this) })
        paginaVoltarFundos.addEventListener('click', function() { mudar_pagina_fundos(this) })
        inputImageProduto.addEventListener('change', function() { readURL(this) })
        inputImageLogo.addEventListener('change', function() { readURL(this) })
        previewButton.addEventListener('click', send_data)
        btnEditarConteudoModelos.addEventListener('click', function() {myColapseModelo.hide(); myColapseFundo.hide();  myColapseConteudo.show()}, false);
        btnEditarConteudoFundos.addEventListener('click', function() {myColapseModelo.hide(); myColapseFundo.hide(); myColapseConteudo.show()}, false);
        btnTrocarModelo.addEventListener('click', function() { removeModelo() }, false);
        btnTrocarFundo.addEventListener('click', function() { removeFundo() }, false);
        btnEscolherModelo.addEventListener('click', function() { escolherModelo(this) }, false);
        btnEscolherFundo.addEventListener('click', function() { escolherFundo(this) }, false);
        formSelector.addEventListener('change', function() { filterModels(this) }, false);
        //tabClicked.addEventListener('click', tabFundosClicked, false);
        //tabClicked.addEventListener('change', function() { tabFundosChange(this) }, false);
        tabClicked.addEventListener('click', tabFundosClicked, false);
        selectorElement.addEventListener('change', function() { selectorChange(this) }, false);
        imgUploadInput.addEventListener('change', setFundoCrop);
        enviarFundoBtn.addEventListener('click', uploadFundoImage);
        
        //imgUploadInput.addEventListener('change', showUploadImage, false);

        divResultadoPesquisa.style.display = 'none'
        wooSpinner.style.display = 'none'
        //imgUploadFeedback.style.display = 'none'

        if(wooActive){
            divImportarProduto.style.display = 'block'
        } else {
            divImportarProduto.style.display = 'none'
        }

        for (var i in background_cfg[0]){
            if (i=='videos'){
                file_type=i;
                changeFundoType()
                break
            }
        }

        function popularInputs(){
            nomeProduto = document.getElementById('importar-nome-produto').innerHTML
            precoNormal = document.getElementById('importar-preco-normal').innerHTML
            precoDesconto = document.getElementById('importar-preco-desconto').innerHTML
            imagemProduto = document.getElementById('importar-imagem-produto').src
            inputNomeProduto.value = nomeProduto
            inputPrecoNormal.value = precoNormal
            inputPrecoDesconto.value = precoDesconto
            imgProduto.src = imagemProduto
            imgProduto.style.display='block'
            wooImported = true
        }

        function pesquisarProduto(){
            wooSpinner.style.display = 'block'
            sku = inputProduto.value
            $.ajax({
                type: 'POST',
                url: '/get_woo_product',
                dataType: 'json',
                data: JSON.stringify({'sku': sku}),
                contentType: 'application/json',
                success: function (data) {
                    if (Object.keys(data).length === 0){
                        window.alert('Produto não encontrado.')
                        divResultadoPesquisa.style.display = 'none'
                        wooSpinner.style.display = 'none'
                    } else{
                        document.getElementById('importar-nome-produto').innerHTML = data['nome_produto']
                        document.getElementById('importar-preco-normal').innerHTML = data['preco_normal']
                        document.getElementById('importar-preco-desconto').innerHTML = data['preco_desconto']
                        document.getElementById('importar-imagem-produto').src = data['imagem_produto']
                        divResultadoPesquisa.style.display = 'block'
                        wooImported = true
                        isImgProdLoaded = true
                        wooSpinner.style.display = 'none'
                    }
                }})
        }
        
        function mudar_pagina_fundos(event){
            if (event.name == 'voltar'){
                pagina -= 1;
                get_fundos(pagina)
            } else if (event.name == 'proximo'){
                pagina += 1;
                get_fundos(pagina)
            }
        }

        function tabFundosClicked(event){
            file_type = event.target.getAttribute('id');
            changeFundoType()
        }

        function changeFundoType(){
            if (file_type!='nav-tabs-file-type'){
                removeOptions(selectorElement);
                addOptions(selectorElement, file_type)
                //pagina = 1;
                //get_fundos(pagina);            
            }
        }

        function get_fundos(pagina){
            $.ajax({
                type: 'POST',
                url: '/get_fundos',
                dataType: 'json',
                data: JSON.stringify({'file_type': file_type, 'tab_id': tab_id, 'pagina': pagina}),
                contentType: 'application/json',
                success: function (data) {
                    fundos = data['fundos']
                    paginasTotal = data['paginasTotal']
                    paginaAtual = data['paginaAtual']
                    paginaNumeroFundos.innerHTML = paginaAtual+" / "+paginasTotal
                    if (paginaAtual == paginasTotal){
                        paginaProximoFundos.style.display = 'none'
                    } else{
                        paginaProximoFundos.style.display = 'block'
                    } 
                    if (paginaAtual == 1){
                        paginaVoltarFundos.style.display = 'none'
                    } else {
                        paginaVoltarFundos.style.display = 'block'
                    }
                    fundos = data['fundos']
                }, async: false})
            if (file_type=='uploads'){
                if (fundos.length==0){
                    uploadBtnResize(showtext=true, absolute=false)
                    uploadBtn.style.display = 'block'
                    selectorElement.style.display = 'none'
                    paginationNav.style.display = 'none'
                }else{
                    uploadBtnResize(showtext=false, absolute=true)
                    selectorElement.style.display = 'block'
                    paginationNav.style.display = 'block'
                    uploadBtn.style.display = 'block'
                }
            }else{   
                uploadBtn.style.display = 'none'         
                selectorElement.style.display = 'block'
                paginationNav.style.display = 'block'
            }
            renderFundos(fundos);
            for (var i = 0; i < cardsFundos.length; i++) {
                cardsFundos[i].addEventListener('click', function() { changeModalFundos(this) }, false);
            }
        }

        // function tabFundosChange(tab_id){
        //     selectorElement.value = tab_id;
        //     pagina = 1;
        //     get_fundos(pagina)
        //     $('.nav-tabs a[id='+tab_id).tab('show');
        // }

        function addOptions(selectElement, file_type) {
            id = 'todos'
            if (id in background_cfg[0][file_type]){
                var opt = document.createElement('option');
                opt.value = id;
                opt.innerHTML = background_cfg[0][file_type][id];
                selectElement.appendChild(opt);
            }
            for (var i in background_cfg[0][file_type]){
                if (i != id){
                    var opt = document.createElement('option');
                    opt.value = i;
                    opt.innerHTML = background_cfg[0][file_type][i];
                    selectElement.appendChild(opt);
                }     
            }
            tab_id=id
            setSelector()
        }

        function removeOptions(selectElement) {
            var i, L = selectElement.options.length - 1;
            for(i = L; i >= 0; i--) {
               selectElement.remove(i);
            }
         }         

        function selectorChange(element){
            tab_id = element.value
            setSelector()
        }

        function setSelector(){
            selectorElement.value = tab_id;
            pagina = 1;
            get_fundos(pagina)
        }

        function colorirModelo(modelo){
            modelo['camadas'].map((camada, i) => 
            {
                if ("cor" in camada){
                    if ('cores' in modelo){
                        cor = modelo['cores'][camada['cor']]
                    } else {
                        cor = modelo['cores_padrao'][camada['cor']]
                    }
                    const rgb = hexToRgb(cor);
                    const color = new Color(rgb[0], rgb[1], rgb[2]);
                    const solver = new Solver(color);
                    const result = solver.solve();
                    var cards = document.getElementsByName(modelo['arte_num'] + '-' + camada['level'])
                    for (i=0; i<cards.length; i++){
                        cards[i].style = result.filter
                    }
                }
            }
            )
        }
        inputDuracao.value = tela.duracao
        duracaoOutput.value = tela.duracao
        if (tela.fundo_id && tela.modelo_id >= 0){
            myColapseConteudo.show()
            myColapseFundo.hide()
            myColapseModelo.hide()
        } else {
            myColapseConteudo.hide()
            if (tela.fundo_id == null){
                myColapseFundo.show()
                myColapseModelo.hide()
                myColapseConteudo.hide()
            } else{
                myColapseModelo.show()
                myColapseFundo.hide()
                myColapseConteudo.hide()
            }
        }

        loadingButton.style.display = 'none'

        var canvasProduto = document.createElement("canvas");
        var ctxProduto = canvasProduto.getContext("2d");

        var canvasLogo = document.createElement("canvas");
        var ctxLogo = canvasLogo.getContext("2d");

        var max_shape = 800
        
        var isImgProdLoaded = false;
        var isImgLogoLoaded = false;
        var wooImported = false;

        function readURL(input) {
            if (input.name == 'product'){
                img = imgProduto
            } else if (input.name == 'logo'){
                img = imgLogo
            }
            if (input.files && input.files[0]) {
                var reader = new FileReader()
                reader.onload = function (e) {
                    img.src = e.target.result
                }
                reader.readAsDataURL(input.files[0])
            }
        }

        imgProduto.onload = function () {
            if (imgProduto.src.substring(0, 5) == "data:"){
                wooImported = false
                isImgProdLoaded = true
                rescale = Math.min(max_shape/this.naturalHeight, max_shape/this.naturalWidth)
                if (rescale < 1){
                    ctxProduto.canvas.width = this.naturalWidth * rescale
                    ctxProduto.canvas.height = this.naturalHeight * rescale
                } else {
                    ctxProduto.canvas.width = this.naturalWidth
                    ctxProduto.canvas.height = this.naturalHeight
                }
                ctxProduto.drawImage(imgProduto, 0, 0, ctxProduto.canvas.width, ctxProduto.canvas.height);
                telaSelection()
            }
        }
        

        imgLogo.onload = function () {
            if (imgLogo.src.substring(0, 5) == "data:"){
                isImgLogoLoaded = true;
                rescale = Math.min(max_shape/this.naturalHeight, max_shape/this.naturalWidth)
                if (rescale < 1){
                    ctxLogo.canvas.width = this.naturalWidth * rescale
                    ctxLogo.canvas.height = this.naturalHeight * rescale
                } else {
                    ctxLogo.canvas.width = this.naturalWidth
                    ctxLogo.canvas.height = this.naturalHeight
                }
                ctxLogo.drawImage(imgLogo, 0, 0, ctxLogo.canvas.width, ctxLogo.canvas.height);
                telaSelection()
            }
        }

        function removeModelo(){
            modeloId = -1
            telaId = tela.id
            $.ajax({
                url: '/escolher_modelo',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'modeloId': modeloId, 'telaId': telaId}),
                contentType: 'application/json',
                success: function (data) {
                    tela = data['tela']
                    telaSelection()
                },
            });
        }

        function removeFundo(){
            fundoId = -1
            fundoTipo = -1
            telaId = tela.id
            $.ajax({
                url: '/escolher_fundo',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'fundoId': fundoId, 'fundoTipo': fundoTipo, 'telaId': telaId}),
                contentType: 'application/json',
                success: function (data) {
                    tela = data['tela']
                    fundo = null;
                    telaSelection()
                },
            });
        }

        function escolherFundo(){
            videoJsFundos.pause();
            fundoId = Number(btnEscolherFundo.name)
            fundoTipo = file_type
            telaId = tela.id

            $.ajax({
                url: '/escolher_fundo',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'fundoId': fundoId, 'fundoTipo': fundoTipo, 'telaId': telaId}),
                contentType: 'application/json',
                success: function (data) {
                    tela = data['tela']
                    fundo = fundos.filter(function(data) {
                        return data.id == tela.fundo_id
                    })[0];
                    telaSelection()
                    myModalFundos.hide()
                    myColapseFundo.hide()
                    if (tela.modelo_id >= 0){
                        myColapseModelo.hide()
                        myColapseConteudo.show()
                    } else {
                        myColapseModelo.show()
                        myColapseConteudo.hide()
                    }
                },
            });
        }

        function escolherModelo(){
            modeloId = Number(btnEscolherModelo.name)
            telaId = tela.id

            $.ajax({
                url: '/escolher_modelo',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'modeloId': modeloId, 'telaId': telaId}),
                contentType: 'application/json',
                success: function (data) {
                    tela = data['tela']
                    telaSelection()
                    myModalModelos.hide()
                    myColapseModelo.hide()
                    if (tela.fundo_id){
                        myColapseFundo.hide()
                        myColapseConteudo.show()
                    } else {
                        myColapseFundo.show()
                        myColapseConteudo.hide()
                    }
                },
            });
        }

        function dataURLtoFile(dataurl, filename) {
 
            var arr = dataurl.split(','),
                mime = arr[0].match(/:(.*?);/)[1],
                bstr = atob(arr[1]), 
                n = bstr.length, 
                u8arr = new Uint8Array(n);
                
            while(n--){
                u8arr[n] = bstr.charCodeAt(n);
            }
            
            return new File([u8arr], filename, {type:mime});
        }

        function send_data(){
            form_data = new FormData(infoForm)

            if (wooImported){
                form_data.append('imgProdFile', imgProduto.src)
            } else{
                var imgProdFile = dataURLtoFile(canvasProduto.toDataURL())
                form_data.set('imgProdFile', imgProdFile);
            }

            form_data.append('isImgProdLoaded', isImgProdLoaded)
            form_data.append('wooImported', wooImported)

            var modelo = modelos.filter(function(data) {
                return data.id == tela.modelo_id
            })[0];
            if ('cores' in modelo){
                form_data.append('cores', modelo['cores'])
            } else {
                form_data.append('cores', modelo['cores_padrao'])
            }
            if ('fontes' in modelo){
                form_data.append('fontes', modelo['fontes'])
            } else {
                form_data.append('fontes', modelo['fontes_padrao'])
            }

            var imgLogoFile = dataURLtoFile(canvasLogo.toDataURL())
            form_data.set('imgLogoFile', imgLogoFile);
            form_data.append('isImgLogoLoaded', isImgLogoLoaded)

            form_data.append('telaId', tela.id)
            
            previewButton.style.display = 'none'
            loadingButton.style.display = 'block'
            $.ajax({
                type: 'POST',
                url: '/parse_data',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                async: true,
                success: function (data) {
                    tela = data['tela']
                    telaSelection()
                    resultImg.style.display = 'block'
                    resultImg.scrollIntoView();
                    previewButton.style.display = 'block'
                    loadingButton.style.display = 'none'
                    isImgProdLoaded = false;
                    isImgLogoLoaded = false;
                }})
        }

        function telaSelection() {
            if (tela.texto_facebook){
                inputFacebook.value = tela.texto_facebook
            }
            if (tela.texto_instagram){
                inputInstagram.value = tela.texto_instagram
            }
            if (tela.texto_nomeempresa){
                inputNomeEmpresa.value = tela.texto_nomeempresa
            }
            if (tela.texto_telefone){
                inputTelefone.value = tela.texto_telefone
            }
            if (tela.texto_email){
                inputEmail.value = tela.texto_email
            }
            if (tela.texto_endereco){
                inputEndereco.value = tela.texto_endereco
            }
            if (tela.texto_mensagem){
                inputMensagem.value = tela.texto_mensagem
                inputMensagem.style.height = (10+inputMensagem.scrollHeight)+"px";
            }
            else{
                inputMensagem.value=""
            }
            if (tela.texto_nomeproduto){
                inputNomeProduto.value = tela.texto_nomeproduto
            }
            if (tela.texto_preconormal){
                inputPrecoNormal.value = tela.texto_preconormal
            }
            if (tela.texto_precodesconto){
                inputPrecoDesconto.value = tela.texto_precodesconto
            }
            if (tela.texto_site){
                inputTextoSite.value = tela.texto_site
            }
            if (isImgProdLoaded){
                imgProduto.style.display='block'
            } else if (tela.imagem_produto) {
                imgProduto.src = tela.imagem_produto;
                imgProduto.style.display='block'
            } else{
                imgProduto.style.display='none'
            }
            if (isImgLogoLoaded){
                imgLogo.style.display='block'
            } else if (tela.imagem_logo) {
                imgLogo.src = tela.imagem_logo;
                imgLogo.style.display='block'
            } else{
                imgLogo.style.display='none'
            }
            if (tela.fundo_id){
                renderFundoEscolhido(fundo)
                divSelecionarFundo.style.display = 'none'
                divFundoEscolhido.style.display = 'block'
                divNaoEditarModelo.style.display = 'none'
            } else {
                pagina = 1;
                get_fundos(pagina)
                divSelecionarFundo.style.display = 'block'
                divFundoEscolhido.style.display = 'none'
                divNaoEditarModelo.style.display = 'block'
                divModeloEscolhido.style.display = 'none'
                divSelecionarModelo.style.display = 'none'
                formSelector.selectedIndex = 0;
            }
            if (tela.modelo_id >= 0 && tela.fundo_id){
                if (tela.preview_gerado){
                    resultImg.src = tela.imagem_preview
                    resultImg.style.display = 'block'
                } else{
                    resultImg.style.display = 'none'
                }
                var modelo = modelos.filter(function(data) {
                    return data.id == tela.modelo_id
                })[0];
                renderModeloEscolhido(modelo, fundo)
                colorirModelo(modelo)
                divSelecionarModelo.style.display = 'none'
                divModeloEscolhido.style.display = 'block'
                
                if ((modelo.atributos).indexOf("texto_facebook") > -1){
                    divFacebook.style.display = 'block'
                } else{
                    divFacebook.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_instagram") > -1){
                    divInstagram.style.display = 'block'
                } else{
                    divInstagram.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_nomeempresa") > -1){
                    divNomeEmpresa.style.display = 'block'
                } else{
                    divNomeEmpresa.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_endereco") > -1){
                    divEndereco.style.display = 'block'
                } else{
                    divEndereco.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_mensagem") > -1){
                    divMensagem.style.display = 'block'
                } else{
                    divMensagem.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_nomeproduto") > -1){
                    divNomeProduto.style.display = 'block'
                } else{
                    divNomeProduto.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_preconormal") > -1){
                    divPrecoNormal.style.display = 'block'
                } else{
                    divPrecoNormal.style.display = 'none'  
                }
                if ((modelo.atributos).indexOf("texto_precodesconto") > -1){
                    divPrecoDesconto.style.display = 'block'
                } else{
                    divPrecoDesconto.style.display = 'none'  
                }
                if ((modelo.atributos).indexOf("texto_site") > -1){
                    divTextoSite.style.display = 'block'
                } else{
                    divTextoSite.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_telefone") > -1){
                    divTextoTelefone.style.display = 'block'
                } else{
                    divTextoTelefone.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("texto_email") > -1){
                    divTextoEmail.style.display = 'block'
                } else{
                    divTextoEmail.style.display = 'none'
                }
                if ((modelo.atributos).indexOf("imagem_produto") > -1){
                    divImagemProduto.style.display = 'block'
                } else{
                    divImagemProduto.style.display = 'none'
                    imgProduto.style.display='none'
                }
                if ((modelo.atributos).indexOf("imagem_logo") > -1){
                    divImagemLogo.style.display = 'block'
                } else{
                    divImagemLogo.style.display = 'none'
                    imgLogo.style.display='none'
                }
            } else {
                if(tela.fundo_id){
                    renderModelos(modelos, fundo)
                    for (i=0; i < modelos.length; i++){
                        colorirModelo(modelos[i])
                    }
                    divSelecionarModelo.style.display = 'block'
                    divModeloEscolhido.style.display = 'none'
                }

            }

            if (tela.fundo_id && tela.modelo_id >= 0){
                divEditarConteudo.style.display = 'block'
                divNaoEditarConteudo.style.display = 'none'
            } else {
                divEditarConteudo.style.display = 'none'
                divNaoEditarConteudo.style.display = 'block'
            }

        for (var i = 0; i < cardsFundos.length; i++) {
            cardsFundos[i].addEventListener('click', function() { changeModalFundos(this) }, false);
            }

        for (var i = 0; i < cardsModelos.length; i++) {
            cardsModelos[i].addEventListener('click', function() { changeModalModelos(this) }, false);
            }
        for (var i = 0; i < btnMudarCor.length; i++) {
            btnMudarCor[i].addEventListener('click', mudarCor, false);
            }
        for (var i = 0; i < btnMudarFonte.length; i++) {
            btnMudarFonte[i].addEventListener('click', mudarFonte, false);
            }
        }

        function mudarFonte(event){
            event.stopPropagation();
            var modelo_id = event.target.name
            const fonteShuffled = fontes.sort(() => 0.5 - Math.random());
            for (var i = 0; i < modelos.length; i++) {
                if(modelos[i].id == modelo_id){
                    let fonteSelected = fonteShuffled.slice(0, modelos[i]['num_fontes']);
                    modelos[i].fontes = fonteSelected
                    modelo =  modelos[i]
                }
            }
            telaSelection()
        }

        function mudarCor(event){
            event.stopPropagation();
            var modelo_id = event.target.name
            const coresShuffled = cores.sort(() => 0.5 - Math.random());
            for (var i = 0; i < modelos.length; i++) {
                if(modelos[i].id == modelo_id){
                    let coresSelected = coresShuffled.slice(0, modelos[i]['num_cores']);
                    modelos[i].cores = coresSelected
                    modelo =  modelos[i]
                }
            }
            colorirModelo(modelo)
        }

        function filterModels(element){          

            if (element.value == 'Todas Categorias'){
                telaSelection()
            }
            else {
                filteredData = modelos.filter(function(data) {
                    return data['labels'].includes(element.value)
                });
                renderModelos(filteredData, fundo)
                for (i=0; i < modelos.length; i++){
                    colorirModelo(modelos[i])
                }
                for (var i = 0; i < cardsModelos.length; i++) {
                    cardsModelos[i].addEventListener('click', function() { changeModalModelos(this) }, false);
                    }
            }


        }

        function changeModalFundos(element){

            var cardId = element.getAttribute("name");
            var JSONelement= fundos.filter(function(data) {
                return data.id == cardId
            })[0];

            if (JSONelement.tipo != 'videos'){
                btnEscolherFundo.name = cardId
                divVideoWrapper.style.display = 'none'
                imgFundoModal.style.display = "block"
                imgFundoModal.src = JSONelement['imagem']
            } else{
                divVideoWrapper.style.display = 'block'
                imgFundoModal.style.display = "none"
                videoJsFundos.src(JSONelement['video']);
                videoJsFundos.play();
                btnEscolherFundo.name = cardId
            }
        }
        
        function changeModalModelos(element){
            var cardId = element.getAttribute("name");

            var modelo = modelos.filter(function(data) {
                return data.id == cardId
            })[0];

            imgFundo.src = fundo.gif
            renderModalModelo(modelo)
            colorirModelo(modelo)
            btnEscolherModelo.name = cardId
            myModalModelos.show()
        }

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

        // Converte a cor em filtros
        class Color {
            constructor(r, g, b) {
              this.set(r, g, b);
            }
            
            toString() {
              return `rgb(${Math.round(this.r)}, ${Math.round(this.g)}, ${Math.round(this.b)})`;
            }
          
            set(r, g, b) {
              this.r = this.clamp(r);
              this.g = this.clamp(g);
              this.b = this.clamp(b);
            }
          
            hueRotate(angle = 0) {
              angle = angle / 180 * Math.PI;
              const sin = Math.sin(angle);
              const cos = Math.cos(angle);
          
              this.multiply([
                0.213 + cos * 0.787 - sin * 0.213,
                0.715 - cos * 0.715 - sin * 0.715,
                0.072 - cos * 0.072 + sin * 0.928,
                0.213 - cos * 0.213 + sin * 0.143,
                0.715 + cos * 0.285 + sin * 0.140,
                0.072 - cos * 0.072 - sin * 0.283,
                0.213 - cos * 0.213 - sin * 0.787,
                0.715 - cos * 0.715 + sin * 0.715,
                0.072 + cos * 0.928 + sin * 0.072,
              ]);
            }
          
            grayscale(value = 1) {
              this.multiply([
                0.2126 + 0.7874 * (1 - value),
                0.7152 - 0.7152 * (1 - value),
                0.0722 - 0.0722 * (1 - value),
                0.2126 - 0.2126 * (1 - value),
                0.7152 + 0.2848 * (1 - value),
                0.0722 - 0.0722 * (1 - value),
                0.2126 - 0.2126 * (1 - value),
                0.7152 - 0.7152 * (1 - value),
                0.0722 + 0.9278 * (1 - value),
              ]);
            }
          
            sepia(value = 1) {
              this.multiply([
                0.393 + 0.607 * (1 - value),
                0.769 - 0.769 * (1 - value),
                0.189 - 0.189 * (1 - value),
                0.349 - 0.349 * (1 - value),
                0.686 + 0.314 * (1 - value),
                0.168 - 0.168 * (1 - value),
                0.272 - 0.272 * (1 - value),
                0.534 - 0.534 * (1 - value),
                0.131 + 0.869 * (1 - value),
              ]);
            }
          
            saturate(value = 1) {
              this.multiply([
                0.213 + 0.787 * value,
                0.715 - 0.715 * value,
                0.072 - 0.072 * value,
                0.213 - 0.213 * value,
                0.715 + 0.285 * value,
                0.072 - 0.072 * value,
                0.213 - 0.213 * value,
                0.715 - 0.715 * value,
                0.072 + 0.928 * value,
              ]);
            }
          
            multiply(matrix) {
              const newR = this.clamp(this.r * matrix[0] + this.g * matrix[1] + this.b * matrix[2]);
              const newG = this.clamp(this.r * matrix[3] + this.g * matrix[4] + this.b * matrix[5]);
              const newB = this.clamp(this.r * matrix[6] + this.g * matrix[7] + this.b * matrix[8]);
              this.r = newR;
              this.g = newG;
              this.b = newB;
            }
          
            brightness(value = 1) {
              this.linear(value);
            }
            contrast(value = 1) {
              this.linear(value, -(0.5 * value) + 0.5);
            }
          
            linear(slope = 1, intercept = 0) {
              this.r = this.clamp(this.r * slope + intercept * 255);
              this.g = this.clamp(this.g * slope + intercept * 255);
              this.b = this.clamp(this.b * slope + intercept * 255);
            }
          
            invert(value = 1) {
              this.r = this.clamp((value + this.r / 255 * (1 - 2 * value)) * 255);
              this.g = this.clamp((value + this.g / 255 * (1 - 2 * value)) * 255);
              this.b = this.clamp((value + this.b / 255 * (1 - 2 * value)) * 255);
            }
          
            hsl() {
              // Code taken from https://stackoverflow.com/a/9493060/2688027, licensed under CC BY-SA.
              const r = this.r / 255;
              const g = this.g / 255;
              const b = this.b / 255;
              const max = Math.max(r, g, b);
              const min = Math.min(r, g, b);
              let h, s, l = (max + min) / 2;
          
              if (max === min) {
                h = s = 0;
              } else {
                const d = max - min;
                s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
                switch (max) {
                  case r:
                    h = (g - b) / d + (g < b ? 6 : 0);
                    break;
          
                  case g:
                    h = (b - r) / d + 2;
                    break;
          
                  case b:
                    h = (r - g) / d + 4;
                    break;
                }
                h /= 6;
              }
          
              return {
                h: h * 100,
                s: s * 100,
                l: l * 100,
              };
            }
          
            clamp(value) {
              if (value > 255) {
                value = 255;
              } else if (value < 0) {
                value = 0;
              }
              return value;
            }
          }
          
          class Solver {
            constructor(target, baseColor) {
              this.target = target;
              this.targetHSL = target.hsl();
              this.reusedColor = new Color(0, 0, 0);
            }
          
            solve() {
              const result = this.solveNarrow(this.solveWide());
              return {
                values: result.values,
                loss: result.loss,
                filter: this.css(result.values),
              };
            }
          
            solveWide() {
              const A = 5;
              const c = 15;
              const a = [60, 180, 18000, 600, 1.2, 1.2];
          
              let best = { loss: Infinity };
              for (let i = 0; best.loss > 25 && i < 3; i++) {
                const initial = [50, 20, 3750, 50, 100, 100];
                const result = this.spsa(A, a, c, initial, 1000);
                if (result.loss < best.loss) {
                  best = result;
                }
              }
              return best;
            }
          
            solveNarrow(wide) {
              const A = wide.loss;
              const c = 2;
              const A1 = A + 1;
              const a = [0.25 * A1, 0.25 * A1, A1, 0.25 * A1, 0.2 * A1, 0.2 * A1];
              return this.spsa(A, a, c, wide.values, 500);
            }
          
            spsa(A, a, c, values, iters) {
              const alpha = 1;
              const gamma = 0.16666666666666666;
          
              let best = null;
              let bestLoss = Infinity;
              const deltas = new Array(6);
              const highArgs = new Array(6);
              const lowArgs = new Array(6);
          
              for (let k = 0; k < iters; k++) {
                const ck = c / Math.pow(k + 1, gamma);
                for (let i = 0; i < 6; i++) {
                  deltas[i] = Math.random() > 0.5 ? 1 : -1;
                  highArgs[i] = values[i] + ck * deltas[i];
                  lowArgs[i] = values[i] - ck * deltas[i];
                }
          
                const lossDiff = this.loss(highArgs) - this.loss(lowArgs);
                for (let i = 0; i < 6; i++) {
                  const g = lossDiff / (2 * ck) * deltas[i];
                  const ak = a[i] / Math.pow(A + k + 1, alpha);
                  values[i] = fix(values[i] - ak * g, i);
                }
          
                const loss = this.loss(values);
                if (loss < bestLoss) {
                  best = values.slice(0);
                  bestLoss = loss;
                }
              }
              return { values: best, loss: bestLoss };
          
              function fix(value, idx) {
                let max = 100;
                if (idx === 2 /* saturate */) {
                  max = 7500;
                } else if (idx === 4 /* brightness */ || idx === 5 /* contrast */) {
                  max = 200;
                }
          
                if (idx === 3 /* hue-rotate */) {
                  if (value > max) {
                    value %= max;
                  } else if (value < 0) {
                    value = max + value % max;
                  }
                } else if (value < 0) {
                  value = 0;
                } else if (value > max) {
                  value = max;
                }
                return value;
              }
            }
          
            loss(filters) {
              // Argument is array of percentages.
              const color = this.reusedColor;
              color.set(0, 0, 0);
          
              color.invert(filters[0] / 100);
              color.sepia(filters[1] / 100);
              color.saturate(filters[2] / 100);
              color.hueRotate(filters[3] * 3.6);
              color.brightness(filters[4] / 100);
              color.contrast(filters[5] / 100);
          
              const colorHSL = color.hsl();
              return (
                Math.abs(color.r - this.target.r) +
                Math.abs(color.g - this.target.g) +
                Math.abs(color.b - this.target.b) +
                Math.abs(colorHSL.h - this.targetHSL.h) +
                Math.abs(colorHSL.s - this.targetHSL.s) +
                Math.abs(colorHSL.l - this.targetHSL.l)
              );
            }
          
            css(filters) {
              function fmt(idx, multiplier = 1) {
                return Math.round(filters[idx] * multiplier);
              }
              return `filter: invert(${fmt(0)}%) sepia(${fmt(1)}%) saturate(${fmt(2)}%) hue-rotate(${fmt(3, 3.6)}deg) brightness(${fmt(4)}%) contrast(${fmt(5)}%);`;
            }
          }
          
          function hexToRgb(hex) {
            // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
            const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
            hex = hex.replace(shorthandRegex, (m, r, g, b) => {
              return r + r + g + g + b + b;
            });
          
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result
              ? [
                parseInt(result[1], 16),
                parseInt(result[2], 16),
                parseInt(result[3], 16),
              ]
              : null;
          }

        telaSelection()

        function setFundoCrop(e){
            if (e.target.files.length) {
                const reader = new FileReader();
                reader.onload = (e)=> {
                    if(e.target.result){
                        let img = document.createElement('img');
                        img.id = 'img-upload-feedback-cropper';
                        img.src = e.target.result
                        imgUploadFeedback.innerHTML = '';
                        imgUploadFeedback.appendChild(img);
                        cropper = new Cropper(img,{
                            'viewMode': 3,
                            'dragMode': 'crop',
                            'zoomable': false,
                            'zoomOnWheel': false,
                            'aspectRatio': 1,
                            'autoCropArea': 1,
                        })
                    }
                };
                reader.readAsDataURL(e.target.files[0]);
            }
        }

        function uploadFundoImage(e){
            e.preventDefault();
            var uploadedImage = dataURLtoFile(cropper.getCroppedCanvas().toDataURL())
            const formData = new FormData();     
            formData.set('uploadedImage', uploadedImage);

            $.ajax('/fundo_upload', {
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success() {
                    myModalUploads.hide()
                    get_fundos(pagina)                    
                }
            });
        }

        // UPLOAD BTN CHANGE TO ICON AND ALIGN
        function uploadBtnResize(showtext=true, absolute=true){
            const icon = '<i class="fas fa-upload" style="color: white"></i>'
            const text = 'Enviar &emsp;'
            if($(window).width() < 767){
                uploadBtn.style.position = 'relative'
                uploadBtn.innerHTML = icon
                if (showtext==true){
                    uploadBtn.innerHTML = text + icon
                }else{
                    uploadBtn.innerHTML = icon
                }

            }else{
                if (absolute==true){
                    uploadBtn.style.position = 'absolute'
                }else{
                    uploadBtn.style.position = 'relative'
                }
                uploadBtn.innerHTML = text + icon
            } 
        }
    }

}

function textAreaAdjust(element) {
    element.style.height = "5px";
    element.style.height = (10+element.scrollHeight)+"px";
}