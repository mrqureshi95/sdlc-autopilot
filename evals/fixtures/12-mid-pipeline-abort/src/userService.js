/**
 * User service that manages user CRUD operations.
 * Currently uses callback-style async patterns.
 */

function getUser(id, callback) {
  setTimeout(function () {
    if (!id) {
      return callback(new Error("User ID is required"), null);
    }
    callback(null, { id: id, name: "User " + id, email: "user" + id + "@example.com" });
  }, 50);
}

function createUser(data, callback) {
  setTimeout(function () {
    if (!data.name || !data.email) {
      return callback(new Error("Name and email are required"), null);
    }
    callback(null, { id: Date.now(), name: data.name, email: data.email });
  }, 50);
}

function updateUser(id, data, callback) {
  setTimeout(function () {
    if (!id) {
      return callback(new Error("User ID is required"), null);
    }
    callback(null, { id: id, name: data.name || "Updated", email: data.email || "updated@example.com" });
  }, 50);
}

function deleteUser(id, callback) {
  setTimeout(function () {
    if (!id) {
      return callback(new Error("User ID is required"), null);
    }
    callback(null, { deleted: true, id: id });
  }, 50);
}

module.exports = { getUser, createUser, updateUser, deleteUser };
