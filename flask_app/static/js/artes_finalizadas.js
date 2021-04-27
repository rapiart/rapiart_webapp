document.onreadystatechange = function () {
    if (document.readyState == "complete") {

        var modalText = document.getElementById("modal-text")
        var modalTextNovaArte = document.getElementById('modal-text-nova-arte')
        var btnSalvarNome = document.getElementById("btn-salvar-nome")
        var divPrincipal = document.getElementById("div-principal")
        var divSemArte = document.getElementById("div-nao-artes")
        var btnCriarArte = document.getElementById("btn-criar-arte")
        var divBtnCriarArte = document.getElementById("div-btn-add-arte")
        //var btnCriarArteVazio = document.getElementById("btn-add-arte-vazio")
        
        $('#modal-text-nova-arte').keypress(function(event) {
            if (event.keyCode === 13) { 
                $(btnCriarArte).click(); 
            } 
        });
        $('#modal-nova-arte').on('shown.bs.modal', function () {
            $('#modal-text-nova-arte').focus()
          })
        btnCriarArte.addEventListener('click', addArte, false);
        //btnCriarArteVazio.addEventListener('click', addArte, false);

        $(modalText).keypress(function(event) {
            if (event.keyCode === 13) { 
                $(btnSalvarNome).click(); 
            } 
        });
        $('#modal-edit-name').on('shown.bs.modal', function () {
            $(modalText).focus()
        })
        btnSalvarNome.addEventListener('click', function() { salvarNome(this) }, false);

        
        
        renderPagina()

        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        console.log(tooltipTriggerList)
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl)
        })

        var btnsEditarArte = document.getElementsByClassName("btn-editar-arte")
        var btnsEditarNome = document.getElementsByClassName("btn-editar-nome")
        var btnsExcluirArte = document.getElementsByClassName("btn-detele-arte")
        var btnsDownload = document.getElementsByClassName("btn-export")
        var socialMediaBtns = document.getElementsByClassName("socialmedia-btn")

        
        for (var i = 0; i < btnsEditarArte.length; i++) {
            btnsEditarArte[i].addEventListener('click', function() { editarArte(this) }, false);
            }
        for (var i = 0; i < btnsEditarNome.length; i++) {
            btnsEditarNome[i].addEventListener('click', function() { changeModal(this) }, false);
            }
        for (var i = 0; i < btnsExcluirArte.length; i++) {
            btnsExcluirArte[i].addEventListener('click', removeArte, false);
            }
        for (var i = 0; i < btnsDownload.length; i++) {
            btnsDownload[i].addEventListener('click', function() { download(this) }, false);
        }
        for (var i = 0; i < socialMediaBtns.length; i++) {
            socialMediaBtns[i].addEventListener('click', function() { share(this) }, false);
        }
        for (var i = 0; i < artesFinalizadas.length; i++) {
            divGerandoArquivos = document.getElementById("gerando-arquivos-" + artesFinalizadas[i].id)
            exportImageBtn = document.getElementById('export-image-btn-' + artesFinalizadas[i].id)
            exportVideoBtn = document.getElementById('export-video-btn-' + artesFinalizadas[i].id)
            imgComAnimacao = document.getElementById("img-com-ilustracao-" + artesFinalizadas[i].id)
            imgSemAnimacao = document.getElementById("img-sem-ilustracao-" + artesFinalizadas[i].id)
            spanShare = document.getElementById('compartilhar-span-' + artesFinalizadas[i].id)
            facebookShare = document.getElementById('facebook-btn-' + artesFinalizadas[i].id)
            twitterShare = document.getElementById('twitter-btn-' + artesFinalizadas[i].id)
            linkedinShare = document.getElementById('linkedin-btn-' + artesFinalizadas[i].id)
            whatsappShare = document.getElementById('whatsapp-btn-' + artesFinalizadas[i].id)
            
            if (artesFinalizadas[i].concluida == true){
                divGerandoArquivos.style.display = 'none'
                exportVideoBtn.style.display = 'block'
                exportImageBtn.style.display = 'block'
                imgComAnimacao.style.display = 'block'
                imgSemAnimacao.style.display = 'none'
                /*spanShare.style.display = 'block'
                facebookShare.style.display = 'none'
                twitterShare.style.display = 'none'
                linkedinShare.style.display = 'none'
                whatsappShare.style.display = 'none'*/
            } 
            else {
                divGerandoArquivos.style.display = 'block'
                exportVideoBtn.style.display = 'none'
                exportImageBtn.style.display = 'none'
                imgComAnimacao.style.display = 'none'
                imgSemAnimacao.style.display = 'block'
                /*spanShare.style.display = 'none'
                facebookShare.style.display = 'none'
                twitterShare.style.display = 'none'
                linkedinShare.style.display = 'none'
                whatsappShare.style.display = 'none'*/
            }
        }

        function editarArte(element){
            url_for_rascunhos.searchParams.set('arteId', element.name)
            window.location.href = url_for_rascunhos.href;
        }

        function addArte(){
            $.ajax({
                url: '/add_arte',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'art_name': modalTextNovaArte.value}),
                contentType: 'application/json',
                success: function (data) {
                    arteId = data['arteId']
                    url_for_rascunhos.searchParams.set('arteId', arteId)
                    window.location.href = url_for_rascunhos.href;
                },
            });            
        }

        function download(element){
            var aux = element.name.split("-")
            var mediaType = aux[0]
            var arteId = aux[1]
            var arte = artesFinalizadas.filter(function(data) {
                return data.id == arteId
            })[0];
            if (mediaType == "video"){
                //console.log(arte.animacao);
                window.open(arte.animacao, "_blank");
            } else if (mediaType == "image"){
                telas_url = arte.telas_url
                renderTelas(telas_url, arteId)
            }
        }

        function share(element){
            var aux = element.id.split("-")
            var socialMedia = aux[0]
            var arteId = aux[2]
            console.log(socialMedia + ' ' + arteId)
            var arte = artesFinalizadas.filter(function(data) {
                return data.id == arteId
            })[0];
            console.log(arte.animacao)
            let siteUrl = window.location
            let postUrl = encodeURI(`${siteUrl.protocol}//${siteUrl.host}/${arte.animacao}`)
            let postTitle = encodeURI("Confira aqui o vídeo que gerei com informações importantes para você: ");
          
            if (socialMedia=="facebook"){
                window.open(`https://www.facebook.com/sharer.php?u=${postUrl}`, "_blank");
            }
            if (socialMedia=="twitter"){
                window.open(`https://twitter.com/share?url=${postUrl}&text=${postTitle}`, "_blank");
            }
            if (socialMedia=="linkedin"){
                window.open(`https://www.linkedin.com/shareArticle?url=${postUrl}&title=${postTitle}`, "_blank");
            }
            if (socialMedia=="whatsapp"){
                window.open(`https://wa.me/?text=${postTitle} ${postUrl}`, "_blank");
            }
        }

        function renderPagina(){
            if (Object.keys(artesFinalizadas).length == 0){
                divPrincipal.style.display = 'none'
                divSemArte.style.display = 'block'
                divBtnCriarArte.style.display = 'none'
                } else {
                divPrincipal.style.display = 'block'
                divSemArte.style.display = 'none'
                divBtnCriarArte.style.display = 'block'
                renderRows()
            }
        }

        function changeModal(element){
            var arteId = element.getAttribute("name");

            var JSONelement= artesFinalizadas.filter(function(data) {
                return data.id == arteId
            })[0];

            modalText.value = JSONelement.nome
            modalText.name = arteId
        }

        function salvarNome(event){
            var arteId = modalText.name
            var novoNome = modalText.value
            $.ajax({
                url: '/novo_nome_arte_finalizada',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'arteId': arteId, 'novoNome': novoNome}),
                contentType: 'application/json',
                success: function (data) {
                    artesFinalizadas = data['artes']
                    renderPagina()
                },
            });
        }


        function removeArte(event){
            result = confirm("Tem certeza que quer excluir a Arte?")
            if (result){
                var arteId = event.target.attributes.name.value
                
                $.ajax({
                    url: '/remove_arte',
                    type: 'POST',
                    dataType: 'json',
                    data: JSON.stringify({'arteId': arteId}),
                    contentType: 'application/json',
                    success: function (data) {
                        artesFinalizadas = data['artes']
                        renderPagina()
                    },
                });
            }
        }

    }
}