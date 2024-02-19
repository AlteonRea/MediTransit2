window.onload = function () {
  updateCartItems();
};

function updateCartItems() {
  var cartItems = JSON.parse(localStorage.getItem("items")) || [];
  var cartItemList = document.getElementById("cartItemList");
  cartItemList.innerHTML = "";

  cartItems.forEach(function (item) {
    var row = cartItemList.insertRow();
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    var cell6 = row.insertCell(5);
    cell1.textContent = item.type.charAt(0).toUpperCase() + item.type.slice(1);
    cell2.textContent = item.name;
    cell3.textContent = item.sizeX;
    cell4.textContent = item.sizeY;
    cell5.textContent = item.sizeZ;
    cell6.textContent = item.quantity;
  });
}
