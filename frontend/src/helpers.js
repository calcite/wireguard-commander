

export const formatDate = function (utcDateString) {
  const localDate = new Date(utcDateString);
  return localDate.toLocaleString();
}

export const camelToWords = function (str) {
  return str.charAt(0).toLowerCase() + str.slice(1).replace(/([A-Z])/g, ' $1').toLowerCase();
}
