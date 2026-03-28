const { getUser, createUser } = require("../userService");

describe("userService", () => {
  test("getUser returns user by id", (done) => {
    getUser(1, (err, user) => {
      expect(err).toBeNull();
      expect(user.id).toBe(1);
      expect(user.name).toBe("User 1");
      done();
    });
  });

  test("getUser returns error for missing id", (done) => {
    getUser(null, (err, user) => {
      expect(err).toBeTruthy();
      expect(err.message).toBe("User ID is required");
      done();
    });
  });

  test("createUser returns new user", (done) => {
    createUser({ name: "Jane", email: "jane@test.com" }, (err, user) => {
      expect(err).toBeNull();
      expect(user.name).toBe("Jane");
      done();
    });
  });
});
