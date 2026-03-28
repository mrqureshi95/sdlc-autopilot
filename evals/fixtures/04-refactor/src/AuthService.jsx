import React, { Component } from "react";

class AuthService extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
      token: null,
      loading: false,
      error: null,
    };
  }

  componentDidMount() {
    const savedToken = localStorage.getItem("auth_token");
    if (savedToken) {
      this.setState({ loading: true });
      this.validateToken(savedToken);
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.token !== this.state.token && this.state.token) {
      localStorage.setItem("auth_token", this.state.token);
    }
  }

  componentWillUnmount() {
    this.isUnmounted = true;
  }

  async validateToken(token) {
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 100));
      if (!this.isUnmounted) {
        this.setState({
          user: { name: "Restored User" },
          token,
          loading: false,
        });
      }
    } catch {
      if (!this.isUnmounted) {
        this.setState({ token: null, loading: false, error: "Invalid token" });
        localStorage.removeItem("auth_token");
      }
    }
  }

  login = async (email, password) => {
    this.setState({ loading: true, error: null });
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 200));
      if (email === "test@example.com" && password === "password") {
        const user = { name: "Test User", email };
        const token = "fake-jwt-token-12345";
        if (!this.isUnmounted) {
          this.setState({ user, token, loading: false });
        }
        return { user, token };
      }
      throw new Error("Invalid credentials");
    } catch (err) {
      if (!this.isUnmounted) {
        this.setState({ loading: false, error: err.message });
      }
      throw err;
    }
  };

  logout = () => {
    localStorage.removeItem("auth_token");
    this.setState({ user: null, token: null, error: null });
  };

  render() {
    return this.props.children({
      user: this.state.user,
      token: this.state.token,
      loading: this.state.loading,
      error: this.state.error,
      login: this.login,
      logout: this.logout,
    });
  }
}

export default AuthService;
