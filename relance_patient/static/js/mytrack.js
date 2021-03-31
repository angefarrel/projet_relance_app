document.addEventListener("DOMContentLoaded", function(){
    //ADD RDV
    'use strict'
    const formAddRDV = document.querySelector(".form-add-rdv");
    const formAddRDVCrsToken = document.querySelector(".form-add-rdv [type='hidden']");
    const rdvDate = document.querySelector(".form-add-rdv #date_rdv");
    const codePatient = document.querySelector(".form-add-rdv #patient_code");
    const motifRdv = document.querySelector(".form-add-rdv #motif");
    // const commentRdv = document.querySelector(".form-add-rdv #")
    if(formAddRDV){
        formAddRDV.addEventListener("submit", function(e) {
            e.preventDefault();

            let constraints={};
            let validators=[];

            constraints = {
            date : {
                    presence: {message:"est réquis", allowEmpty:false}
                },

            code_patient:{
                presence: {message:"est requis", allowEmpty:false},
                format:{
                    pattern:"[0-9]{4}[\/][0-9]{2}[\/][0-9]{2}[\/][0-9]{5}",
                    flags:"gi",
                    message:"n'est pas correct"
                }
            },
            motif:{
                presence:{message:"est requis !", allowEmpty:false}
            },
            // comment={
            //     presence:{message:"est requis", allowEmpty:false}
            // }
            }

            validators = validate({
                date:rdvDate.value,
                code_patient:codePatient.value,
                motif:motifRdv.value,
                // comment:commentRdv,
            }, constraints)
            if (validators === undefined){
                loader.style.display = 'flex'
                const url = formAddRDV.getAttribute("action")
                fetch(url, {
                    method: "POST",
                    body: new FormData(formAddRDV),
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": formAddRDVCrsToken.value,
                    }
                }).then(res => res.json())
                .then(data => {
                    loader.style.display = 'none'
                    if(data.type == "error") {
                        Swal.fire({
                            type: "error",
                            title: "Création échouée",
                            text: data.error.message
                        })
                    }else if(data.type == "success") {
                        Swal.fire({
                            title: 'Création réussie',
                            text: data.message,
                            type: 'success',
                          }).then((result) => {
                            if (result.value) {
                              window.location.href = data.redirectLink.link
                            }
                          }).catch(err => {
                            loader.style.display = 'none'
                            Swal.fire({
                                type: "error",
                                title: "Erreur",
                                text: "Une erreur est survenue, veuillez réessayer!"
                            })
                        })
                    }
                })
            }
            else{
                for (const error in validators) {
                    if(error === "date") {
                        rdvDate.classList.add("error")
                        rdvDate.nextElementSibling.textContent = validators[error][0]
                    }

                    if(error === "code_patient") {
                        codePatient.classList.add("error")
                        codePatient.nextElementSibling.textContent = validators[error][0]
                    }
                    if(error === "motif") {
                        const motifBox = document.querySelector(".vsb-main button");
                        oldStyle.borderColor = "red!important"; 
                        motifRdv.nextElementSibling.textContent = validators[error][0];
                    }
                }
                return false
            }
     })
    }


 //   ADD INDEX TESTING

        const formAddIndex=document.querySelector(".form-add-index")
        const formAddIndexCrsToken = document.querySelector(".form-add-index [type='hidden']");
        const indexCodePatient=document.querySelector(".form-add-index #patient_code")
        const indexTypeContact=document.querySelector(".form-add-index #type_contact")
        const indexSexeContact=document.querySelector(".form-add-index #sexe_contact")
        const dateNaissanceIndex=document.querySelector(".form-add-index #date_naissance")
        const statutIdenIndex=document.querySelector(".form-add-index #statut_identification")
        if(formAddIndex){
            formAddIndex.addEventListener("submit", function(e){
                e.preventDefault();

                let constraints = {};
                let validators = [];
                constraints={
                    code_patient:{
                        presence:{message:" est requis !", allowEmpty:false},
                        format:{
                            pattern:"[0-9]{4}[\/][0-9]{2}[\/][0-9]{2}[\/][0-9]{5}",
                            flags:"gi",
                            message:" n'est pas correct !"
                        }
                    },
                    contact_type:{
                        presence:{message:" est requis !", allowEmpty:false}
                    },
                    sex_contact:{
                        presence:{message:"est requis", allowEmpty:false}
                    },
                    birthdate:{
                     presence:{message:"est requis !", alloxEmpty:false}
                     },
                    ident_status:{
                     presence:{message:"est requis !", allowEmpty:false}
                     },
                }
                validators = validate({
                    code_patient:indexCodePatient.value,
                    contact_type:indexTypeContact.value,
                    sex_contact:indexSexeContact.value,
                    birthdate:dateNaissanceIndex.value,
                    ident_status:statutIdenIndex.value,
                }, constraints)
                if(validators===undefined){
                    loader.style.display = 'flex'
                    const url = formAddIndex.getAttribute("action")
                    fetch(url, {
                        method: "POST",
                        body: new FormData(formAddIndex),
                        headers: {
                            "Accept": "application/json",
                            "X-CSRFToken": formAddIndexCrsToken.value,
                        }
                    }).then(res => res.json())
                    .then(data => {
                        loader.style.display = 'none'
                        if(data.type == "error") {
                            Swal.fire({
                                type: "error",
                                title: "Création échouée",
                                text: data.error.message
                            })
                        }else if(data.type == "success") {
                            Swal.fire({
                                title: 'Création réussie',
                                text: data.message,
                                type: 'success',
                              }).then((result) => {
                                if (result.value) {
                                  window.location.href = data.redirectLink.link
                                }
                              }).catch(err => {
                                loader.style.display = 'none'
                                Swal.fire({
                                    type: "error",
                                    title: "Erreur",
                                    text: "Une erreur est survenue, veuillez réessayer!"
                                })
                            })
                        }
                    })
                }
                else{
                    for (const error in validators) {

                        if(error === "code_patient") {
                            indexCodePatient.classList.add("error")
                            indexCodePatient.nextElementSibling.textContent = validators[error][0]
                        }

                        if(error === "contact_type") {
                            indexTypeContact.classList.add("error")
                            indexTypeContact.nextElementSibling.textContent = validators[error][0]
                        }
                        if(error === "sex_contact") {
                            indexSexeContact.classList.add("error")
                            indexSexeContact.nextElementSibling.textContent = validators[error][0]
                        }
                        if(error === "ident_stauts") {
                            const motifBox = document.querySelector(".vsb-main button");
                            oldStyle.borderColor = "red!important"; 
                            statutIdenIndex.nextElementSibling.textContent = validators[error][0];
                        }
                        }
                    return false
                    }
                })}

// ADD RESPECT

        const formAddRespect=document.querySelector(".form-add-respect")
        const formAddRespectCrsToken=document.querySelector(".form-add-respect [type='hidden']")
        const respectLastRdv=document.querySelector(".form-add-respect #last_rdv")
        const respectDate=document.querySelector(".form-add-respect #date_venue")
        const respectCodePatient=document.querySelector(".form-add-respect #patient_code")
        const respectMotif=document.querySelector(".form-add-respect #motif")
        const respectComment=document.querySelector(".form-add-respect #respect_comment")
        if(formAddRespect){
            formAddRespect.addEventListener("submit", function(e){
                e.preventDefault();

                let constraints={};
                let validators=[];
                constraints={
                last_rdv:{
                        presence:{message:"est requis !", allowEmpty:false}
                    },
                date_venue:{
                    presence:{message:"est requis !", allowEmpty:false}
                },
                patient_code:{
                    presence:{message:"est requis !", allowEmpty:false},
                    format:{
                        pattern:"[0-9]{4}[\/][0-9]{2}[\/][0-9]{2}[\/][0-9]{5}",
                        flags:"gi",
                        message:" n'est pas correct !"
                    }
                },
                motif:{
                    presence:{message:"est requis !", allowEmpty:false}
                },
                // comment:{
                //     presence:{message:"est requis !", allowEmpty:true}
                // },
                }
                validators=validate({
                    last_rdv:respectLastRdv.value,
                    date_venue:respectDate.value,
                    patient_code:respectCodePatient.value,
                    motif:respectMotif.value,
                    comment:respectComment.value,
                }, constraints)
                if(validators===undefined){
                    loader.style.display = 'flex'
                    const url = formAddRespect.getAttribute("action")
                    fetch(url, {
                        method:"POST",
                        body:new FormData(formAddRespect),
                        headers : {
                            "Accept": "application/json",
                            "X-CSRFToken" : formAddRespectCrsToken.value,
                        }
                    }).then(res => res.json())
                    .then(data => {
                        loader.style.display = 'none'
                        if(data.type == "error") {
                            Swal.fire({
                                type: "error",
                                title: "Création échouée",
                                text: data.message
                            })
                        } else if(data.type == "success") {
                            Swal.fire({
                                title: 'Création réussie',
                                text: data.message,
                                type: 'success',
                              }).then((result) => {
                                if (result.value) {
                                  window.location.href = data.redirectLink.link
                                }
                        }).catch(err => {
                            loader.style.display = 'none'
                            Swal.fire({
                                type: "error",
                                title: "Erreur",
                                text: "Une erreur est survenue, veuillez réessayer!"
                            })
                        })
                    }
                })
            }
            else{
                for  (const error in validators){
                    if (error === "last_rdv") {
                        respectLastRdv.classList.add("error")
                        respectLastRdv.nextElementSibling.textContent = validators["error"][0]
                    }

                    if (error === "date_venue") {
                        respectDate.classList.add("error")
                        respectDate.nextElementSibling.textContent = validators["error"][0]
                    }

                    if(error === "patient_code") {
                        respectCodePatient.classList.add("error")
                        respectCodePatient.nextElementSibling.textContent = validators[error][0]
                    }

                    if(error === "motif") {
                        const motifBox = document.querySelector(".vsb-main button");
                        oldStyle.borderColor = "red!important";
                        respectMotif.nextElementSibling.textContent = validators[error][0]
                    }

                    // if(error === "comment") {
                    //     respectComment.classList.add("error")
                    //     respectComment.nextElementSibling.textContent = validators[error][0]
                    // }
                }
                return false
            }})}

                document.querySelectorAll(".form-add-index input").forEach(elment => {
                    elment.addEventListener("focus", () => {
                        if(elment.type == "text" || elment.type == "date") {
                            elment.classList.remove('error')
                            elment.nextElementSibling.textContent = ""
                        }
                    })
                })
                document.querySelectorAll(".form-add-rdv input").forEach  (elment => {
                    elment.addEventListener("focus", () => {
                        if(elment.type == "text" || elment.type == "date") {
                            elment.classList.remove('error')
                            elment.nextElementSibling.textContent = ""
                        }
                    })
                })
                document.querySelectorAll(".form-add-respect input").forEach  (elment => {
                    elment.addEventListener("focus", () => {
                        if(elment.type == "text" || elment.type == "date") {
                            elment.classList.remove('error')
                            elment.nextElementSibling.textContent = ""
                        }
                    })
                })

        // const formSearchIndex=document.querySelector(".form-search-index")
        // const searchIndex=document.querySelector(".form-search-index #code_patient")
        // // const formSearchIndexCsrfToken=document.querySelector(".form-search-index [type='hidden']")
        // if(formSearchIndex){
        //     formSearchIndex.addEventListener("submit", function(e){
        //         e.preventDefault();

        //         let constraints={};
        //         let validators=[]
        //         constraints={
        //             patient_code:{
        //                 presence:{message:"est requis !", allowEmpty:false},
        //                 format:{
        //                     pattern:"[0-9]{4}[\/][0-9]{2}[\/][0-9]{2}[\/][0-9]{5}",
        //                     // flags="gi",
        //                     message:"n'est pas correct"
        //                 }
        //             }
        //         }
        //         validators=validate({
        //             patient_code:searchIndex.value,
        //         }, constraints)
        //         console.log(validators)
        //         if(validators){
        //             for(const error in validators){
        //                 if(error === "patient_code"){
        //                     searchIndex.classList.add("error")
        //                     searchIndex.nextElementSibling.textContent = validators[error][0]
        //                 }}
        //         }
        //     })
        // }
   })