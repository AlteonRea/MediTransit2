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
    quantity: 1,
  };

  var cart = JSON.parse(localStorage.getItem("items")) || [];
  cart.push(newItem);
  localStorage.setItem("items", JSON.stringify(cart));

  document.getElementById("itemForm").reset();
  alert("Item added to cart successfully!");

  updateCartPopup();
}

function clearCart() {
  localStorage.removeItem("items");
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
  var cartItems = JSON.parse(localStorage.getItem("items")) || [];

  containersList.classList.contains("active")
    ? renderItems(cartItems, true)
    : renderItems(cartItems, false);
}

function createDivWithClass(className, textContent = null) {
  const element = document.createElement("div");
  element.className = className;
  if (textContent !== null) {
    element.textContent = textContent;
  }
  return element;
}

function createDivWithId(id) {
  const div = document.createElement("div");
  div.id = id;
  return div;
}

function updateLocalStorage(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

function renderItems(items, containerActive) {
  const cartItemGroup = document.getElementById("cartItemGroup");
  cartItemGroup.innerHTML = "";

  items.forEach((item, index) => {
    if (
      (containerActive === true && item.type === "goods") ||
      (containerActive === false && item.type === "container")
    ) {
      return;
    }

    const cartItem = createDivWithClass("cartItem");
    const itemDetail = createDivWithClass("item-detail");
    const itemName = createDivWithClass("itemName", item.name);

    const itemSize = createDivWithClass("itemSize");
    itemSize.innerHTML = `
      <div>X: ${item.sizeX}</div>
      <div>Y: ${item.sizeY}</div>
      <div>Z: ${item.sizeZ}</div>
    `;

    itemDetail.append(itemName, itemSize);
    const itemQty = createDivWithClass("item-qty");
    const qtyText = createDivWithClass("qty-text", "Quantity");

    const changeQty = createDivWithClass("change-qty");
    const subQty = createDivWithId("subQty");
    subQty.innerHTML = `<i class="fa-solid fa-minus"></i>`;

    const quantity = document.createElement("p");
    quantity.textContent = item.quantity;

    const addQty = createDivWithId("addQty");
    addQty.innerHTML = `<i class="fa-solid fa-plus"></i>`;

    changeQty.append(subQty, quantity, addQty);

    const removeItem = createDivWithId("removeItem");
    removeItem.innerHTML = `<i class="fa-solid fa-trash"></i>`;

    itemQty.append(qtyText, changeQty, removeItem);
    cartItem.append(itemDetail, itemQty);
    cartItemGroup.appendChild(cartItem);

    const hr = document.createElement("hr");
    cartItemGroup.appendChild(hr);

    subQty.addEventListener("click", () => {
      if (item.quantity > 1) {
        item.quantity--;
        quantity.textContent = item.quantity;
        updateLocalStorage("items", items);
      }
    });

    addQty.addEventListener("click", () => {
      item.quantity++;
      quantity.textContent = item.quantity;
      updateLocalStorage("items", items);
    });

    removeItem.addEventListener("click", () => {
      items.splice(index, 1);
      updateLocalStorage("items", items);
      renderItems(items);
    });
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
