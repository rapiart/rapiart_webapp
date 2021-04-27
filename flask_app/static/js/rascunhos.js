document.onreadystatechange = function () {
    if (document.readyState == "complete") {

        renderizarAcordeao(arte)
        renderCards(telas, arte.id)
        updateButonsTelas()

        new bootstrap.Collapse(document.getElementById("collapse-telas-" + arte.id))

        var previewBtn = document.getElementById("preview-btn-" + arte.id)
        var divVideo = document.getElementById("div-video-" + arte.id)
        var btnAddTela = document.getElementById("btn-add-tela-" + arte.id)
        var afterLoad = document.getElementById("after-load-" + arte.id)
        var divLoading = document.getElementById("animacao-loading-" + arte.id)
        var btnExcluirArte = document.getElementById("btn-detele-arte" + arte.id)
        var generateAnimation = document.getElementById("btn-generate-video-" + arte.id)
        var audioSelection = document.getElementById("audio-selector-"+ arte.id)
        var btnSalvarNome = document.getElementById("btn-salvar-nome-" + arte.id)
        var artesCollapse = document.getElementsByClassName("accordion-collapse")
        var audio = document.getElementById("player-" + arte.id);
        var videoToFocus = document.getElementById("col1-editar-conteudo");
        var videoJs = videojs("div-video-" + arte.id);
        //videoJs.aspectRatio('1:1');
        videoJs.fluid(true);
        var btnCompartilhar = document.getElementById("btn-compartilhar");

        divVideo.style.display='none'
        afterLoad.style.display = 'none'
        divLoading.style.display = 'none'

        musica = document.getElementById("arte-" + arte.id + '-' + arte.audio_id)
        musica.classList.add('item_highlight')
        
        btnAddTela.addEventListener('click', createTela, false);
        btnExcluirArte.addEventListener('click', removeArte, false);
        generateAnimation.addEventListener('click', createAnimation, false);
        audioSelection.addEventListener('click', audioSelect, false);

        $('#novo-nome-'+ arte.id).keypress(function(event) {
            if (event.keyCode === 13) { 
                $(btnSalvarNome).click(); 
            } 
        });
        $('#editName-' + arte.id).on('shown.bs.modal', function () {
            $('#novo-nome-'+ arte.id).focus()
          })

        btnSalvarNome.addEventListener('click', salvarNome, false)
        
        for (var i = 0; i < artesCollapse.length; i++) {
            artesCollapse[i].addEventListener('hidden.bs.collapse', pauseAudio, false);
        }
        
        function audioSelect(event) {
            clicked_element = document.getElementById(event.target.getAttribute('id'))
            highlighted_element = document.querySelectorAll('.item_highlight'); 
            
            [].forEach.call(highlighted_element, function(el) {
                el.classList.remove('item_highlight');
            });
            clicked_element.classList.add('item_highlight');

            var sourceUrl = event.target.getAttribute('value');
            var arteId = event.target.getAttribute('name');

            var audio = document.getElementById("player-" + arteId);
            var source = document.getElementById("mp3_src-" + arteId);
            
            audio.pause();
            
            if (sourceUrl) {
                source.src = sourceUrl;
                audio.load();
                audio.play();
            }
        }

        function pauseAudio(event){
            audio.pause();
            videoJs.pause();
        }

        function salvarNome(event){
            var arteId = event.target.attributes.name.value
            var novoNome = document.getElementById("novo-nome-"+ arteId).value
            $.ajax({
                url: '/novo_nome_rascunho',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'arteId': arteId, 'novoNome': novoNome}),
                contentType: 'application/json',
                success: function (data) {
                    arte = data['arte']
                    telas = data['telas']
                    renderizarAcordeao(arte)
                    renderCards(telas, arte.id)
                    updateButonsTelas()
                },
            });
        }


    function updateButonsTelas(){
        var delButons = document.getElementsByClassName("del-btn");
        var moveButons = document.getElementsByClassName("move-btn");
        var copyButons = document.getElementsByClassName("copy-btn");
        
        for (var i = 0; i < delButons.length; i++) {
            delButons[i].removeEventListener('click', removeCard, false);
            delButons[i].addEventListener('click', removeCard, false);
            }

        for (var i = 0; i < moveButons.length; i++) {
            moveButons[i].removeEventListener('click', moveCard, false);
            moveButons[i].addEventListener('click', moveCard, false);
            }

        for (var i = 0; i < copyButons.length; i++) {
            copyButons[i].removeEventListener('click', copyCard, false);
            copyButons[i].addEventListener('click', copyCard, false);
            }
    } 

    function createAnimation(event){
        pauseAudio(event)
        var arteId = document.querySelectorAll('.item_highlight')[0].getAttribute('name')
        var audioId = document.querySelectorAll('.item_highlight')[0].getAttribute('audio-id')

        afterLoad.style.display = 'none'
        previewBtn.style.display = 'none'
        divLoading.style.display = 'block'
        $.ajax({
            url: '/generate_animation',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'arteId': arteId, 'audioId': audioId}),
            contentType: 'application/json',
            success: function (data) {
                videoJs.src(data['animacao_src']);
                btnCompartilhar.href = data['animacao_src']
                divLoading.style.display = 'none'
                afterLoad.style.display = 'block'
                previewBtn.style.display = 'block'
                divVideo.style.display = 'block';
                videoToFocus.scrollIntoView();
                videoJs.play();
            },
        });
    }

    function removeArte(event){
        result = confirm("Tem certeza que quer excluir a arte?")
        if (result){
            var arteId = event.target.attributes.name.value
            
            $.ajax({
                url: '/remove_arte',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'arteId': arteId}),
                contentType: 'application/json',
                success: function (data) {
                    window.location.href = url_for_artes.href;
                },
            });
        }
    }

    function createTela(event){
        var arteId = event.target.attributes.name.value
        
        $.ajax({
            url: '/criar_tela',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'arteId': arteId}),
            contentType: 'application/json',
            success: function (data) {
                telas = data['telas']
                renderCards(telas, arte.id)
                updateButonsTelas()
            },
        });
    }


    function copyCard(event){
        var info = (event.target.attributes.name.value).split('-')

        var arteId = info[0]
        var telaId = info[1]

        $.ajax({
            url: '/copiar_tela',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'arteId': arteId, 'telaId':telaId}),
            contentType: 'application/json',
            success: function (data) {
                telas = data['telas']
                renderCards(telas, arte.id)
                updateButonsTelas()
            },
        });

    }

    function removeCard(event){
        result = confirm("Tem certeza que quer excluir a Tela?")
        if (result) {
            var info = (event.target.attributes.name.value).split('-')

            var arteId = info[0]
            var telaId = info[1]
    
            $.ajax({
                url: '/excluir_tela',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({'arteId':arteId, 'telaId':telaId}),
                contentType: 'application/json',
                success: function (data) {
                    telas = data['telas']
                    renderCards(telas, arte.id)
                    updateButonsTelas()
                },
            });
        }
    }

    function moveCard(event){
        var info = (event.target.attributes.name.value).split('-')

        var arteId = info[0]
        var telaId = info[1]
        var direction = event.target.getAttribute("direction")
        if (direction==null){
            direction = event.target.parentElement.getAttribute("direction")
        }
        
        $.ajax({
            url: '/mover_tela',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'arteId':arteId, 'telaId':telaId, 'direction':direction}),
            contentType: 'application/json',
            success: function (data) {
                telas[arteId] = data
                renderCards(telas[arteId], arteId)
                updateButonsTelas()
            },
        })
    }

    }
}