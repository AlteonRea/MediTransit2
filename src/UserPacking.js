window.onload = function () {
  updateCartItems();
};

function updateCartItems() {
  var cartItems = JSON.parse(localStorage.getItem("cart")) || [];
  var cartItemList = document.getElementById("cartItemList");
  cartItemList.innerHTML = "";

  cartItems.forEach(function (item) {
    var row = cartItemList.insertRow();
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    cell1.textContent = item.name;
    cell2.textContent = item.sizeX;
    cell3.textContent = item.sizeY;
    cell4.textContent = item.sizeZ;
    cell5.textContent = item.type;
  });
}
