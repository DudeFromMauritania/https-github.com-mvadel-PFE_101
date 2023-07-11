document.addEventListener("DOMContentLoaded", function() {
  // Get all transaction buttons
  var transactionBtns = document.querySelectorAll(".transaction-btn");

  // Add click event listener to each transaction button
  transactionBtns.forEach(function(btn) {
      btn.addEventListener("click", function() {
          // Get the corresponding transaction details element
          var transactionDetails = this.nextElementSibling;

          // Toggle the display of transaction details
          if (transactionDetails.style.display === "none") {
              transactionDetails.style.display = "block";
          } else {
              transactionDetails.style.display = "none";
          }
      });
  });

});

window.jsPDF = window.jspdf.jsPDF;
      
function downloadPDF() {
  var username = document.getElementById('username').textContent;
  var privateKey = document.getElementById('private-key').textContent;
  var publicKey = document.getElementById('public-key').textContent;

  var doc = new window.jsPDF();
  var fontSize = 12;
  var lineHeight = 15;
  var content = `
    <-- Username -->: ${username}
    <-- Private Key -->:\n${privateKey}
    <-- Public Key -->:\n${publicKey}
  `;

  doc.setFontSize(fontSize);
  doc.text(content, 5, 10);
  doc.save('user_keys.pdf');
}
