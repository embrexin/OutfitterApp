export async function loginUser(email, password) {
  console.log("Login request:", email, password);
  return { success: true }; // fake login
}

export async function signupUser(email, password) {
  console.log("Signup request:", email, password);
  return { success: true }; // fake signup
}
