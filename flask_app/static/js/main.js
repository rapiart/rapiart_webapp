document.onreadystatechange = function () {
    if (document.readyState == "complete") {
        
        function generate_png(){
            var form_data = new FormData(svgForm)
    
            $.ajax({
                type: 'POST',
                url: '/image_generator',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                async: true,
                success: function (data) {
                    svgPath = data['svg_path']
                    innerHtml = 'url("data:image/png;base64,' + data['bytes'] + '")'
                    imageDiv.style.backgroundImage = innerHtml
                    imageSectionDiv.style.display="block"                
                }})
    
        }
    
        function send_data(){
            form_data = new FormData(infoForm)
            form_data.append('svg_path', svgPath)
            $.ajax({
                type: 'POST',
                url: '/parse_data',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                async: true,
                success: function (data) {
                    console.log(data)
                    innerHtml = 'url("data:image/png;base64,' + data + '")'
                    resultDiv.style.backgroundImage = innerHtml
                    resultSectionDiv.style.display="block"                
                }})
        }
    
        var svgPath = null
    
        var svgForm = document.getElementById('svg-upload')
        var infoForm = document.getElementById('info-upload')
    
        var imageSectionDiv = document.getElementById('img-sec')
        var resultSectionDiv = document.getElementById('res-sec')
        var imageDiv = document.getElementById('imagePreview')
        var resultDiv = document.getElementById('resultPreview')
        var svgButton = document.getElementById('input-svg')
        var infoButton = document.getElementById('button-submit')
    
        infoButton.addEventListener('click', send_data)
        svgButton.addEventListener('change', generate_png)

  }
}
