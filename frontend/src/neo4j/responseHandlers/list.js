const handleListResponse = (response) => {
  const { data } = response;

  if (data.results[0].data.length === 0) {
    throw new Error('Response is empty.');
  }
  // TODO: add more error handling

  return data.results[0].data.map(d => d.row[0]);
};

export default handleListResponse;
