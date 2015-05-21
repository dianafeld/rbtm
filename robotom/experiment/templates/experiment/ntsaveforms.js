(function ntSaveForms() {
 var text, cl;
 $(".ntSaveForms").each(function(i) {
 cl = "ntSaveForms"+i;
 $(this).addClass(cl); // add new class
 text = $.Storage.get(cl);
 if (text && text.length > 0 && !$(this).val()) {
 $(this).val(text); // set field data
 }
 });

$(".ntSaveForms").keyup(function() {
 $.Storage.set($(this).attr("class").split(" ")[$(this).attr("class").split(" ").length -1], $(this).val()); // save field data
 });

$(".ntSaveFormsSubmit").click(function() {
 $(".ntSaveForms").each(function(i) {
 $.Storage.remove("ntSaveForms"+i); // remove data
 });
 });
})();
