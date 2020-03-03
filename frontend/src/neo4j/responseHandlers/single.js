const handleSingleResponse = (response) => {
  const { data } = response;

  if (data.results[0].data.length === 0) {
    throw new Error('Response is empty.');
  }
  // TODO: add more error handling

  return data.results[0].data[0].row[0];
};

export default handleSingleResponse;
