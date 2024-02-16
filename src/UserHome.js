function addItem() {
  var itemName = document.getElementById("itemName").value;
  var sizeX = document.getElementById("sizeX").value;
  var sizeY = document.getElementById("sizeY").value;
  var sizeZ = document.getElementById("sizeZ").value;
  var itemType = document.getElementById("itemType").value;

  if (
    itemName.trim() === "" ||
    sizeX.trim() === "" ||
    sizeY.trim() === "" ||
    sizeZ.trim() === ""
  ) {
    alert("Please fill in all fields.");
    return;
  }

  var newItem = {
    name: itemName,
    sizeX: sizeX,
    sizeY: sizeY,
    sizeZ: sizeZ,
    type: itemType,
  };

  var cart = JSON.parse(localStorage.getItem("cart")) || [];
  cart.push(newItem);
  localStorage.setItem("cart", JSON.stringify(cart));

  document.getElementById("itemForm").reset();
  alert("Item added to cart successfully!");

  updateCartPopup();
}

function clearCart() {
  localStorage.removeItem("cart");
  updateCartPopup();
  alert("Cart cleared!");
}

function checkEnter(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    addItem();
  }
}

var containersList = document.getElementById("containersList");
var goodsList = document.getElementById("goodsList");

function activateContainerGroup() {
  containersList.classList.add("active");
  goodsList.classList.remove("active");
  updateCartPopup();
}

function activateGoodsGroup() {
  goodsList.classList.add("active");
  containersList.classList.remove("active");
  updateCartPopup();
}

function updateCartPopup() {
  var cartItems = JSON.parse(localStorage.getItem("cart")) || [];

  // Separate items into containers and goods
  var containers = cartItems.filter((item) => item.type === "container");
  var goods = cartItems.filter((item) => item.type === "goods");

  containersList.classList.contains("active")
    ? renderItems(containers)
    : renderItems(goods);
}

function renderItems(items) {
  var cartItemGroup = document.getElementById("cartItemGroup");

  cartItemGroup.innerHTML = "";

  items.forEach((item) => {
    var cartItem = document.createElement("div");
    cartItem.className = "cartItem";
    var itemName = document.createElement("div");
    itemName.className = "itemName";
    itemName.textContent = item.name;

    var itemSize = document.createElement("div");
    itemSize.className = "itemSize";
    itemSize.innerHTML = `
      <div>X: ${item.sizeX}</div>
      <div>Y: ${item.sizeY}</div>
      <div>Z: ${item.sizeZ}</div>
    `;

    cartItem.appendChild(itemName);
    cartItem.appendChild(itemSize);

    cartItemGroup.appendChild(cartItem);

    var hr = document.createElement("hr");
    cartItemGroup.appendChild(hr);
  });
}

function toggleCartPopup() {
  var cartPopup = document.getElementById("cartPopup");
  if (cartPopup.classList.contains("show")) {
    cartPopup.classList.remove("show");
  } else {
    cartPopup.classList.add("show");
  }
}

window.onload = function () {
  document
    .getElementById("cartIcon")
    .addEventListener("click", toggleCartPopup);
  updateCartPopup();
};

document.querySelector(".cartItemGroup").addEventListener("wheel", (event) => {
  event.preventDefault();
  const scrollAmount = 80;
  if (event.deltaY > 0) {
    document.querySelector(".cartItemGroup").scrollBy({
      top: scrollAmount,
      behavior: "smooth",
    });
  } else {
    document.querySelector(".cartItemGroup").scrollBy({
      top: -scrollAmount,
      behavior: "smooth",
    });
  }
});
