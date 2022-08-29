function createDoughnutChart(labels, data, text, label, element_id){
    const m_chart = new Chart(document.getElementById(element_id), {
        type: 'doughnut',
        data: {
        labels: labels,
        datasets: [
            {
            label: label,
            backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9"],
            data: data
            }
        ]
        },
        options: {
        title: {
            display: true,
            text: text
        }
        }
    });
}

var random_number = Math.floor(100000000 + Math.random() * 900000000);
// Delete view
// Get table tr elements 

function DeleteItems(element_id, delete_url, redirect_url, refresh_page=false){
    
    var selected_rows=[];
    var array_rows=[];
    
    $(element_id).find('tr').each(function(){
        var row=$(this);
        console.log(row.find('input[type="checkbox"]').is(':checked'));
        if (row.find('input[type="checkbox"]').is(':checked')) {
            // console.log(row.attr('data-id'));
            selected_rows.push(row.attr('data-id'));
            array_rows = selected_rows;

        };
    });

    var selected_rows = JSON.stringify(selected_rows);
   
    $.ajax({
        url: delete_url,
        type: 'POST',
        data: {'check_box_item_ids': selected_rows,
        'csrfmiddlewaretoken': $("[name=csrfmiddlewaretoken]").val()},
        success: function () {
            if (refresh_page == true){
                location.reload();
            }else{
                 // Refreh element
            $(element_id).load(location.href + " " + element_id);
            }
           

            console.log('Item apagado');
            // window.location.href = redirect_url;
            
            if (array_rows.length > 0){
                $( "<div class='alert alert-warning p-0 m-0' id='alert_id" + random_number + "' role='alert'>" + 
                    " <button type='button' class='btn close' style='vertical-align: center;" + 
                    "horizontal-align: right;' data-dismiss='alert' aria-label='Close' " +
                    "<span aria-hidden='True' onclick='Hide(alert_id" + random_number + ")'>&times;</span>" +
                    "</button> Item(s) deleted successfully</div>" ).insertBefore( ".page-breadcrumb" );
            };

            $("#alert_id" + random_number).delay(3200).hide(300);
            random_number = Math.floor(100000000 + Math.random() * 900000000);
        },
    })
};

function printDocument(){
    var prtContent = document.getElementById("section-to-print");
    var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
    WinPrint.document.write(prtContent.innerHTML);
    WinPrint.document.close();
    WinPrint.focus();
    WinPrint.print();
    WinPrint.close();
  }

  function printDocumentClass(){
    var prtContent = document.getElementsByClassName("section-to-print");
    var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
    WinPrint.document.write(prtContent.innerHTML);
    WinPrint.document.close();
    WinPrint.focus();
    WinPrint.print();
    WinPrint.close();
  }

$(document).ready(function() {

    console.log("document ready.")

    var random_number = Math.floor(100000000 + Math.random() * 900000000);
    if ($('#id_component_no').val() == ""){ 
        $('#id_component_no').val(random_number);
    }
    
    if ($('#id_allocation_no').val() == ""){
        $('#id_allocation_no').val(random_number);
    }

    if ($('#id_order').val() == ""){
        $('#id_order').val(random_number);
    }

    $('#checkall').click(function () {
        $('.rowcheckbox').prop('checked', this.checked);
    });

    $('.rowcheckbox').click(function () {
        if ($('#checkall').prop('checked', true)) {
            $('#checkall').prop('checked', false)
        }

    });
   
     // Use DataTables to display table
var table = $('#sortTableExtraLarger').DataTable({
        buttons: [
            'copy', 'excel', 'pdf'
        ],
        columnDefs: [
            { orderable: false, targets: 0 },
            { orderable: false, targets: 7 },
            { "width": "1%", "targets": 0 }
        ],
        order: [[1, 'asc']],
        responsive: {
            breakpoints: [
              {name: 'bigdesktop', width: Infinity},
              {name: 'meddesktop', width: 1480},
              {name: 'smalldesktop', width: 1280},
              {name: 'medium', width: 1188},
              {name: 'tabletl', width: 1024},
              {name: 'btwtabllandp', width: 848},
              {name: 'tabletp', width: 768},
              {name: 'mobilel', width: 480},
              {name: 'mobilep', width: 320}
            ]
          },
        "scrollX": true
    });

    table.buttons().container()
    .appendTo('#ExtraButtons');

    // Use DataTables to display table
  var table_2 = $('#sortTableExtraLarge').DataTable({
        
        buttons: [
            'copy', 'excel', 'pdf'
        ],
        columnDefs: [
            { orderable: false, targets: 0 },
            { orderable: false, targets: 6 },
            { "width": "1%", "targets": 0 }
        ],
        order: [[1, 'asc']],
        responsive: {
            breakpoints: [
              {name: 'bigdesktop', width: Infinity},
              {name: 'meddesktop', width: 1480},
              {name: 'smalldesktop', width: 1280},
              {name: 'medium', width: 1188},
              {name: 'tabletl', width: 1024},
              {name: 'btwtabllandp', width: 848},
              {name: 'tabletp', width: 768},
              {name: 'mobilel', width: 480},
              {name: 'mobilep', width: 320}
            ]
          },
        "scrollX": true
    });

    table_2.buttons().container()
    .appendTo('#ExtraButtons');

    // Use DataTables to display table
  var table_3 =  $('#sortTableLarge').DataTable({
        
        buttons: [
            'copy', 'excel', 'pdf'
        ],
        columnDefs: [
            { orderable: false, targets: 0 },
            { orderable: false, targets: 5 },
            { "width": "1%", "targets": 0 }
        ],
        order: [[1, 'asc']],
        "scrollX": true,
        responsive: {
            breakpoints: [
              {name: 'bigdesktop', width: Infinity},
              {name: 'meddesktop', width: 1480},
              {name: 'smalldesktop', width: 1280},
              {name: 'medium', width: 1188},
              {name: 'tabletl', width: 1024},
              {name: 'btwtabllandp', width: 848},
              {name: 'tabletp', width: 768},
              {name: 'mobilel', width: 480},
              {name: 'mobilep', width: 320}
            ]
          }
    });

    table_3.buttons().container()
    .appendTo('#ExtraButtons');

     // Use DataTables to display table
    var table_4 =  $('#sortTableMedium').DataTable({
        stateSave: true,
        "bFilter" : true,
        "iDisplayLength": 10,
        
        buttons: [
            'copy', 'excel', 'pdf'
        ],
        columnDefs: [
            { orderable: false, targets: 0 },
            { orderable: false, targets: 4 },
            { "width": "1%", "targets": 0 }
        ],
        order: [[1, 'asc']],
        responsive: true,
        "scrollX": true
        
    });

    table_4.buttons().container()
    .appendTo('#ExtraButtons');
     // Use DataTables to display table
    
   var table_5 =  $('#sortTableSmall').DataTable({
        
        buttons: [
            'copy', 'excel', 'pdf'
        ],
        columnDefs: [
            { orderable: false, targets: 0 },
            { orderable: false, targets: 3 },
            { "width": "1%", "targets": 0 }
        ],
        order: [[1, 'asc']],
        responsive: true,
        "scrollX": true
    });

    table_5.buttons().container()
    .appendTo('#ExtraButtons');
     
    // Use DataTables to display table
var table_6 =  $('#sortTableSmaller').DataTable({
        
        buttons: [
            'copy', 'excel', 'pdf'
        ],
        columnDefs: [
            { "width": "1%", "targets": 0 }
        ],
        order: [[1, 'asc']],
        responsive: true,
        "scrollX": true
    });  
    
    table_6.buttons().container()
    .appendTo('#ExtraButtons');

});

function findTotal(){
    var sum = 0;
    console.log(sum);

		//iterate through each textboxes and add the values
		$('input[name="amount"]').each(function() {

			//add only if the value is number
			if(!isNaN(this.value) && this.value.length!=0) {
				sum += parseFloat(this.value);
			}

		});
  
		//.toFixed() method will roundoff the final sum to 2 decimal places
        var total = parseFloat($('#total_value').val());
        console.log(total);
        if (sum > total){
            var change = sum - total;
            $('input[name="change"]').val(change.toFixed(2));
        }
        else{
            $('input[name="change"]').val(0);
        }
};

function Hide(HideID) 
{
    HideID.style.display = "none"; 
}

var html = '';
html += '<div id="inputFormRow" class="row m-0 p-0">' 
html += '<div class="form-group col-md-12 mb-0">' 
html += '<div id="div_id_action" class="mb-3">' 
html += '<label for="id_action" class="form-label requiredField">'
html += 'Action<span class="asteriskField">*</span>' 
html += '</label>' 
html += '<div class="input-group">' 
html += '<input type="text" name="action" maxlength="255" class="textInput form-control" required id="id_action">'
html += '<button  class="btn btn fa fa-minus-circle" id="removeRow" type="button"></button>'
html += '</div>' 
html += '</div>' 
html += '</div>' 
html += '</div>'      

// add row dynamically
$("#button-id-add_action").click(function () {
    $('#add_action').append(html);
    // $('#div_id_action').clone().appendTo('#formRow');
});

// remove row dynamically
$(document).on('click', '#removeRow', function () {
    $(this).closest('#inputFormRow').remove();
});

var item_html = '';
item_html += '<div id="itemFormRow" class="row m-0 p-0">'
item_html += '<div class="form-group col-md-6 mb-0" >' 
item_html += '<div id="div_id_item" class="mb-3">' 
item_html += '<label for="id_item" class="form-label requiredField">'
item_html += 'Item<span class="asteriskField">*</span>' 
item_html += '</label>' 
item_html += '<input type="text" name="item" maxlength="255" class="textinput textInput form-control" required id="id_item">' 
item_html += '</div>' 
item_html += '</div>' 
item_html += '<div class="form-group col-md-2 m-0" >' 
item_html += '<div id="div_id_cost" class="mb-3">' 
item_html += '<label for="id_cost" class="form-label requiredField">'
item_html += 'Cost<span class="asteriskField">*</span>' 
item_html += '</label>' 
item_html += '<input type="number" name="cost" value="0" step="0.01" class="numberinput form-control" required id="id_cost">' 
item_html += '</div>' 
item_html += '</div>' 
item_html += '<div class="form-group col-md-2 m-0" >' 
item_html += '<div id="div_id_quantity" class="mb-3">' 
item_html += '<label for="id_quantity" class="form-label requiredField">'
item_html += 'Quantity<span class="asteriskField">*</span>' 
item_html += '</label>' 
item_html += '<input type="number" name="quantity" value="0" step="0.01" class="numberinput form-control" required id="id_quantity">' 
item_html += '</div>' 
item_html += '</div>' 
item_html += '<div class="mb-3 form-group col-md-2 m-0"  id="div_id_item">' 
item_html += '<label for="id_unit" class="form-label  requiredField">'
item_html += 'Unit<span class="asteriskField">*</span>' 
item_html += '</label>' 
item_html += '<div>' 
item_html += '<div class="input-group">' 
item_html += '<select name="unit" class="select form-control" id="id_unit">' 
item_html += '<option value="Cm">Cm</option> <option value="Kg">Kg</option>' 
item_html += '<option value="L">L</option> <option value="Gb">Gb</option>' 
item_html += '<option value="Mb">Mb</option> <option value="Piece" selected>Piece</option>' 
item_html += '<option value="M³">M3</option> <option value="Km">Km</option>' 
item_html += '<option value="G">G</option>'
item_html += '</select>' 
item_html += '<button  class="btn btn fa fa-minus-circle" id="removeItem" type="button"></button>' 
item_html += '</div>' 
item_html += '</div>'
item_html += '</div>'
item_html += '</div>'

 // add row
$("#button-id-add_item").click(function () {
    $('#item_row').append(item_html);
    // $('#div_id_action').clone().appendTo('#formRow');
});

// remove row
$(document).on('click', '#removeItem', function () {
    $(this).closest('#itemFormRow').remove();
});


function fillTax(){
    console.log('A jobar....')
    var product = $('#id_product').val();
    
    $.ajax({
        type: "POST",
        url: "#",
        data: { csrfmiddlewaretoken: '{{ csrf_token }}', text: text },  
        success: function callback(response){
                   /* do whatever with the response */
        alert(response);
        } 
    })
}


function cloneProduct(url){
    var newWindow = window.open(url);

    $( newWindow ).on( "load", function() {
        var doc = newWindow.document;
        const id_code = $('#id_code').text();
        const id_name = $('#id_name').text();
        const id_type = $('#id_type').text();
        const id_parent = $('#id_parent').text();
        const id_tax = $('#id_tax').text();
        const id_warehouse = $('#id_warehouse').text();
        const id_description = $('#id_description').text();
        const id_barcode = $('#id_barcode').text();
        const id_sell_price = $('#id_sell_price').text();
        const id_min_sell_price = $('#id_min_sell_price').text();
        const id_sell_price2 = $('#id_sell_price2').text();
        const id_sell_price3 = $('#id_sell_price3').text();
        const id_sell_price4 = $('#id_sell_price4').text();
        const id_sell_price5 = $('#id_sell_price5').text()
        const id_purchase_price = $('#id_purchase_price').text();
        const id_max_purchase_price = $('#id_max_purchase_price').text();
        const id_physical_stock = $('#id_physical_stock').text();
        const id_stock_limit = $('#id_stock_limit').text();
        const id_desired_stock = $('#id_desired_stock').text();
        const id_image = $('#id_image').text();
        const id_product_nature = $('#id_product_nature').text();
        const id_product_url = $('#id_product_url').text();
        const id_weight = $('#id_weight').text();
        const id_length = $('#id_length').text();
        const id_width = $('#id_width').text();
        const id_height = $('#id_height').text();
        const id_length_units = $('#id_length_units').text();
        const id_area = $('#id_area').text();
        const id_area_units = $('#id_area_units').text();
        const id_volume = $('#id_volume').text();
        const id_volume_units = $('#id_volume_units').text();
        const id_weight_units = $('#id_weight_units').text();
        const id_active_status = $('#id_active_status').text();
        const id_sell_status = $('#id_sell_status').text();
        const id_purchase_status = $('#id_purchase_status').text();
        const id_notes = $('#id_notes').text();

        console.log(id_weight);

        var year =  new Date().getSeconds();
        $('#id_code', doc).val(id_code.trim() + year ); 
        $('#id_name', doc).val(id_name.trim() + " CLONE" ); 
        // $('#id_type', doc).val(id_type.trim()); 
        // $('#id_parent', doc).val(id_parent.trim()); 
        // $('#id_tax', doc).text(id_tax.trim());
        // $('#id_warehouse', doc).text(id_warehouse.trim()); 
        $('#id_description', doc).val(id_description.trim()); 
        $('#id_barcode', doc).val(id_barcode.trim()); 
        $('#id_sell_price', doc).val(id_sell_price); 
        $('#id_min_sell_price', doc).val(id_min_sell_price.trim()); 
        $('#id_sell_price2', doc).val(parseFloat(id_sell_price2.trim())); 
        $('#id_sell_price3', doc).val(id_sell_price3.trim()); 
        $('#id_sell_price4', doc).val(id_sell_price4.trim()); 
        $('#id_sell_price5', doc).val(id_sell_price5.trim()); 
        $('#id_purchase_price', doc).val(id_purchase_price.trim()); 
        $('#id_max_purchase_price', doc).val(id_max_purchase_price.trim()); 
        $('#id_physical_stock', doc).val(id_physical_stock.trim()); 
        $('#id_stock_limit', doc).val(id_stock_limit.trim()); 
        $('#id_desired_stock', doc).val(id_desired_stock.trim()); 
        $('#id_image', doc).val(id_image.trim()); 
        $('#id_product_nature', doc).val(id_product_nature.trim()); 
        $('#id_product_url', doc).val(id_product_url.trim()); 
        $('#id_weight', doc).val(id_weight.trim()); 
        $('#id_length', doc).val(id_length.trim()); 
        $('#id_width', doc).val(id_width.trim()); 
        $('#id_height', doc).val(id_height.trim()); 
        $('#id_length_units', doc).val(id_length_units.trim()); 
        $('#id_area', doc).val(id_area.trim()); 
        $('#id_area_units', doc).val(id_area_units.trim()); 
        $('#id_volume', doc).val(id_volume.trim()); 
        $('#id_volume_units', doc).val(id_volume_units.trim()); 
        $('#id_weight_units', doc).val(id_weight_units.trim()); 
        // $('#id_active_status', doc).val(id_active_status.trim()); 
        // $('#id_sell_status', doc).val(id_sell_status.trim()); 
        // $('#id_purchase_status', doc).val(id_purchase_status.trim()); 
        $('#id_notes', doc).val(id_notes.trim());                 
    });

};

function cloneMaintenance(url){
    const maitenance_name = $( "h1" ).text();
    const type = $( "#type" ).text();
    const frequency = $( "#frequency" ).text();
    const time_allocated = $( "#time_allocated" ).text();
    const schedule = $( "#schedule" ).text();
    const time_schedule = $( "#time_schedule" ).text();

    var newWindow = window.open(url);

    $( newWindow ).on( "load", function() {
        
        newWindow.document.getElementById('id_name').value = maitenance_name;
        newWindow.document.getElementById('id_type').value = "" + type;
        newWindow.document.getElementById('id_frequency').value = parseFloat(frequency);
        newWindow.document.getElementById('id_time_allocated').value = parseFloat(time_allocated);
        newWindow.document.getElementById('id_schedule').value = "" + schedule;
        newWindow.document.getElementById('id_time_schedule').value = "" + time_schedule;
        
        var doc = newWindow.document;
        var item = $("#item_row", doc);
        var action = $("#add_action", doc);
        var i = 0;
        var x = 0;
        var itemMainArray = [];
        var actionMainArray = [];
                        
        $('#sortTableSmaller tr').each(function() {
            if (!this.rowIndex) return; // skip first row
            
            x += 1;
            html = $(html);

            $('#id_action', $(html)).addClass('actionClass')
            
            action.append(html);
            
            var actionName = this.cells[1].innerHTML;
            var actionNotes = this.cells[2].innerHTML;
            
            $('#id_action', doc).val(actionName);
            $('#id_notes', doc).val(actionNotes);

            var internalArray = [];

            internalArray.push(actionName);
            internalArray.push(actionNotes);
            
            actionMainArray.push(internalArray);

        });

        $('.actionClass', doc).each(function(i, obj) {
            data = actionMainArray[i];
            $(this).val(data[i]);
        });

        $('#sortTableSmall tr').each(function() {
            if (!this.rowIndex) return; // skip first row
            
            i += 1;

            item_html = $(item_html);

            $('#id_item', $(item_html)).addClass('itemClass')
            $('#id_cost', item_html).addClass('costClass')
            $('#id_quantity', item_html).addClass('quantityClass')
            $('#id_unit', item_html).addClass('unitClass')
            
            item.append(item_html);
            
            var itemName = this.cells[1].innerHTML;
            var itemCost = this.cells[2].innerHTML;
            var itemQuantity = this.cells[3].innerHTML;
            var itemUnit = this.cells[4].innerHTML;

            $('#id_item', doc).val(itemName);
            $('#id_cost', doc).val(parseFloat(itemCost));
            $('#id_quantity', doc).val(parseFloat(itemQuantity));
            $('#id_unit', doc).val(itemUnit.trim());
            
            var internalArray = [];

            internalArray.push(itemName);
            internalArray.push(itemCost);
            internalArray.push(itemQuantity);
            internalArray.push(itemUnit);

            itemMainArray.push(internalArray);

        });

        $('.itemClass', doc).each(function(i, obj) {
            data = itemMainArray[i];
            $(this).val(data[i]);
        });

        $('.costClass', doc).each(function(i, obj) {
            data = itemMainArray[i];
            console.log(data[1]);
            $(this).val(parseFloat(data[1]));
        });

        $('.quantityClass', doc).each(function(i, obj) {
            data = itemMainArray[i];
            console.log(data[2]);
            $(this).val(parseFloat(data[2]));
        });

        $('.unitClass', doc).each(function(i, obj) {
            data = itemMainArray[i];
            console.log(data[3]);
            $(this).val((data[3]).toString().trim());
        });
    });
} 

$("#id_product").change(function () {
    
    var productId = $(this).val();  // get the selected product ID from the HTML input
    
    $.ajax({                       // initialize an AJAX request
    url: "/ajax/load-prices/",     // set the url of the request (= localhost:8000/ajax/load-prices/)
    data: {
        'product': productId       // add the product id to the GET parameters
    },
    
    success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#list__price_list").html(data);  // replace the contents of the prices input with the data that came from the server
        
        $('#id_price').val($("#sell_price_option").val().replace(",", ".")); // replace the price and replaces commas by point
        $('#id_quantity').val(1); // replace the quantity
        $('#id_type').val($("#type").val()); // replace the product Type
        
        $('#id_tax').val($("#tax").val()); // replace the tax
    }
});
});

// Makes product combombox searchable, createbla and clearable
dselect(document.querySelector('#id_product'),{
    search: true,
    creatable: true,
    clearable: true
    });

 //Create PDf from HTML...
 function CreatePDFfromHTML() {
    var HTML_Width = $(".html-content").width();
    var HTML_Height = $(".html-content").height();
    var top_left_margin = 15;
    var PDF_Width = HTML_Width + (top_left_margin * 2);
    var PDF_Height = (PDF_Width * 1.5) + (top_left_margin * 2);
    var canvas_image_width = HTML_Width;
    var canvas_image_height = HTML_Height;

    var totalPDFPages = Math.ceil(HTML_Height / PDF_Height) - 1;

    html2canvas($(".html-content")[0]).then(function (canvas) {
        var imgData = canvas.toDataURL("image/jpeg", 1.0);
        var pdf = new jsPDF('p', 'pt', [PDF_Width, PDF_Height]);
        pdf.addImage(imgData, 'JPG', top_left_margin, top_left_margin, canvas_image_width, canvas_image_height);
        for (var i = 1; i <= totalPDFPages; i++) { 
            pdf.addPage(PDF_Width, PDF_Height);
            pdf.addImage(imgData, 'JPG', top_left_margin, -(PDF_Height*i)+(top_left_margin*4),canvas_image_width,canvas_image_height);
        }
        var random_number = Math.floor(100000000 + Math.random() * 900000000);
        pdf.save("document - " + random_number + ".pdf");
        /* $(".html-content").hide(); */
    });
}

